from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from .catalog import Catalog
from .shared import NumType, Provider


class SpatialExtent(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#spatial-extent-object
    """

    bbox: List[List[NumType]]


class TimeInterval(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#temporal-extent-object
    """

    interval: List[List[Union[str, None]]]


class Extent(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#extent-object
    """

    spatial: SpatialExtent
    temporal: TimeInterval


class Stats(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#stats-object
    """

    min: Union[NumType, str]
    max: Union[NumType, str]


class Collection(Catalog):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md
    """

    license: str
    extent: Extent
    title: Optional[str]
    keywords: Optional[List[str]]
    providers: Optional[List[Provider]]
    summaries: Optional[Dict[str, Union[Stats, List[Any]]]]
