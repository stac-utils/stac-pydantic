from datetime import datetime as dt
from typing import Dict, List, Optional, Union

from geojson_pydantic.features import Feature, FeatureCollection
from pydantic import AnyUrl, Field, constr, root_validator, validator
from pydantic.datetime_parse import parse_datetime

from stac_pydantic.api.extensions.context import ContextExtension
from stac_pydantic.links import Links
from stac_pydantic.shared import DATETIME_RFC339, Asset, BBox, StacCommonMetadata
from stac_pydantic.version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#properties-object
    """

    datetime: Union[dt, str] = Field(..., alias="datetime")

    @validator("datetime")
    def validate_datetime(cls, v, values):
        if v == "null":
            if not values["start_datetime"] and not values["end_datetime"]:
                raise ValueError(
                    "start_datetime and end_datetime must be specified when datetime is null"
                )

        if isinstance(v, str):
            return parse_datetime(v)

        return v

    class Config:
        extra = "allow"
        json_encoders = {dt: lambda v: v.strftime(DATETIME_RFC339)}


class Item(Feature):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    """

    id: constr(min_length=1)
    stac_version: constr(min_length=1) = Field(STAC_VERSION, const=True)
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: Links
    stac_extensions: Optional[List[AnyUrl]]
    collection: Optional[str]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)

    @root_validator(pre=True)
    def validate_bbox(cls, values):
        if values.get("geometry") and values.get("bbox") is None:
            raise ValueError("bbox is required if geometry is not null")
        return values


class ItemCollection(FeatureCollection):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/itemcollection-spec.md
    """

    stac_version: constr(min_length=1) = Field(STAC_VERSION, const=True)
    features: List[Item]
    stac_extensions: Optional[List[AnyUrl]]
    links: Links
    context: Optional[ContextExtension]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
