from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from stac_pydantic.catalog import Catalog
from stac_pydantic.shared import Asset, NumType, Provider, StacBaseModel


class SpatialExtent(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#spatial-extent-object
    """

    bbox: List[List[NumType]]


class TimeInterval(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#temporal-extent-object
    """

    interval: List[List[Union[str, None]]]


class Extent(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#extent-object
    """

    spatial: SpatialExtent
    temporal: TimeInterval


class Range(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#stats-object
    """

    minimum: Union[NumType, str]
    maximum: Union[NumType, str]


class Collection(Catalog):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md
    """

    assets: Optional[Dict[str, Asset]] = None
    license: str = Field(..., alias="license", min_length=1)
    extent: Extent
    title: Optional[str] = None
    keywords: Optional[List[str]] = None
    providers: Optional[List[Provider]] = None
    summaries: Optional[Dict[str, Union[Range, List[Any], Dict[str, Any]]]] = None
    type: str = "Collection"  # type:ignore

    @field_validator("type")
    @classmethod
    def type_value(cls, v: str) -> str:
        if v != "Collection":
            raise ValueError("Field `type` must be `Collection`")
        return v
