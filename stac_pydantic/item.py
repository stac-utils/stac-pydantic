from datetime import datetime as dt
from typing import Dict, List, Optional, Union

from geojson_pydantic.features import Feature, FeatureCollection
from pydantic import Field, BaseModel, root_validator, ValidationError

from .shared import Asset, BBox, ExtensionTypes, Link
from .extensions import Extensions
from .version import STAC_VERSION


def _parse_loc(loc):
    if isinstance(loc, tuple):
        path = " -> ".join(loc)
    else:
        path = loc
    return f"properties -> {path}"


class ItemProperties(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.9.0/item-spec/item-spec.md#properties-object
    """

    datetime: Union[str, dt] = Field(..., alias="datetime")
    # stac common metadata (https://github.com/radiantearth/stac-spec/blob/v0.9.0/item-spec/common-metadata.md)
    title: Optional[str] = Field(None, alias="title")
    description: Optional[str] = Field(None, alias="description")
    start_datetime: Optional[Union[str, dt]] = Field(None, alias="start_datetime")
    end_datetime: Optional[Union[str, dt]] = Field(None, alias="end_datetime")
    platform: Optional[str] = Field(None, alias="platform")
    instruments: Optional[List[str]] = Field(None, alias="instruments")
    constellation: Optional[str] = Field(None, alias="constellation")
    mission: Optional[str] = Field(None, alias="mission")


    class Config:
        extra = "allow"


class Item(Feature):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.9.0/item-spec/item-spec.md
    """

    id: str
    stac_version: str = Field(STAC_VERSION, const=True)
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: List[Link]
    bbox: BBox
    stac_extensions: Optional[List[Union[str, ExtensionTypes]]]
    collection: Optional[str]

    @root_validator(pre=True)
    def validate_extensions(cls, values):
        errors = []
        if "stac_extensions" in values:
            for ext in values["stac_extensions"]:
                if ext != "checksum":
                    ext_model = Extensions.get(ext)
                    try:
                        ext_model(**values["properties"])
                    except ValidationError as e:
                        raw_errors = e.raw_errors
                        for error in raw_errors:
                            if isinstance(error, list):
                                for err in error[0]:
                                    err._loc = _parse_loc(err._loc)
                            else:
                                error._loc = _parse_loc(error._loc)
                        errors += e.raw_errors
        if errors:
            raise ValidationError(errors=errors, model=Item)

        return values

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


class ItemCollection(FeatureCollection):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.9.0/item-spec/itemcollection-spec.md
    """

    stac_version: str = Field(STAC_VERSION, const=True)
    features: List[Item]
    stac_extensions: Optional[List[ExtensionTypes]]
    links: Optional[List[Link]]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
