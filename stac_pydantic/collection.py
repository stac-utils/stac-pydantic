from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AfterValidator, Field, conlist
from typing_extensions import Annotated

from stac_pydantic.catalog import _Catalog
from stac_pydantic.shared import (
    Asset,
    BBox,
    NumType,
    Provider,
    StacBaseModel,
    UtcDatetime,
)


def validate_time_interval(v):  # noqa: C901
    ivalues = iter(v)

    # The first time interval always describes the overall temporal extent of the data.
    overall_interval = next(ivalues, None)
    if not overall_interval:
        return v

    start, end = overall_interval
    if start and end:
        if start > end:
            raise ValueError(f"`Start` time {start} older than `End` time {end}")

    # All subsequent time intervals can be used to provide a more precise
    # description of the extent and identify clusters of data.
    for s, e in ivalues:
        if s and e:
            if s > e:
                raise ValueError(f"`Start` time {s} older than `End` time {e}")

        if start and s:
            if start > s:
                raise ValueError(
                    f"`Overall Start` time {start} older than `Start` time {s}"
                )

        if end and e:
            if e > end:
                raise ValueError(
                    f"`End` time {e} older than `Overall Start` time {end}"
                )

    return v


class SpatialExtent(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#spatial-extent-object
    """

    bbox: List[BBox]


class TimeInterval(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#temporal-extent-object
    """

    interval: Annotated[  # type: ignore
        conlist(
            conlist(Union[UtcDatetime, None], min_length=2, max_length=2),
            min_length=1,
        ),
        AfterValidator(validate_time_interval),
    ]


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


class Collection(_Catalog):
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
    type: Literal["Collection"]
