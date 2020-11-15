from datetime import datetime as dt
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Type, Union

from geojson_pydantic.features import Feature, FeatureCollection
from pydantic import BaseModel, Field, create_model, validator
from pydantic.fields import FieldInfo

from .api.extensions.context import ContextExtension
from .api.extensions.paging import PaginationLink
from .extensions import Extensions
from .shared import Asset, BBox, Link, StacCommonMetadata
from .utils import decompose_model
from .version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/item-spec.md#properties-object
    """

    datetime: Union[str, dt] = Field(..., alias="datetime")

    @validator("datetime")
    def validate_datetime(cls, v, values):
        if v == "null":
            if not values["start_datetime"] and not values["end_datetime"]:
                raise ValueError(
                    "start_datetime and end_datetime must be specified when datetime is null"
                )
        return v

    class Config:
        extra = "allow"


class Item(Feature):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/item-spec.md
    """

    id: str
    stac_version: str = Field(STAC_VERSION, const=True)
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: List[Link]
    bbox: BBox
    stac_extensions: Optional[List[str]]
    collection: Optional[str]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


class ItemCollection(FeatureCollection):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/itemcollection-spec.md
    """

    stac_version: str = Field(STAC_VERSION, const=True)
    features: List[Item]
    stac_extensions: Optional[List[str]]
    links: List[Union[PaginationLink, Link]]
    context: Optional[ContextExtension]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


@lru_cache()
def _extension_model_factory(
    stac_extensions: Tuple[str], base_class: Type[Item], skip_remote_refs: bool = False
) -> Tuple[Type[BaseModel], FieldInfo]:
    """
    Create a stac item properties model for a set of stac extensions
    """
    fields = decompose_model(base_class.__fields__["properties"].type_)
    for ext in stac_extensions:
        if skip_remote_refs and ext.startswith("http"):
            continue
        if ext == "checksum":
            continue
        fields.update(decompose_model(Extensions.get(ext)))
    return (
        create_model("CustomItemProperties", __base__=ItemProperties, **fields),
        FieldInfo(...),
    )


def item_model_factory(
    item: Dict, skip_remote_refs: bool = False, base_class: Type[Item] = Item
) -> Type[BaseModel]:
    """
    Create a pydantic model based on the extensions used by the item
    """
    item_fields = decompose_model(base_class)
    stac_extensions = item.get("stac_extensions")

    if stac_extensions:
        item_fields["properties"] = _extension_model_factory(
            tuple(stac_extensions), base_class, skip_remote_refs
        )

    return create_model("CustomStacItem", **item_fields, __base__=base_class)


def validate_item(item: Dict, reraise_exception: bool = False, **kwargs) -> bool:
    """
    Wrapper around ``item_model_factory`` for stac item validation
    """
    try:
        item_model_factory(item, **kwargs)(**item)
    except Exception:
        if reraise_exception:
            raise
        return False
    return True
