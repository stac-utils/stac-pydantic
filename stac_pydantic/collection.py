from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

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
    validate_bbox,
)

if TYPE_CHECKING:
    StartEndTime = List[Union[UtcDatetime, None]]
    TInterval = List[StartEndTime]
else:
    StartEndTime = conlist(Union[UtcDatetime, None], min_length=2, max_length=2)
    TInterval = conlist(StartEndTime, min_length=1)


def validate_bbox_interval(v: List[BBox]) -> List[BBox]:
    ivalues = iter(v)

    # The first time interval always describes the overall spatial extent of the data.
    overall_bbox = next(ivalues, None)
    if not overall_bbox:
        return v

    assert validate_bbox(overall_bbox)

    if len(overall_bbox) == 4:
        xmin, ymin, xmax, ymax = overall_bbox
    else:
        xmin, ymin, _, xmax, ymax, _ = overall_bbox

    crossing_antimeridian = xmin > xmax
    for bbox in ivalues:
        _ = validate_bbox(bbox)

        if len(bbox) == 4:
            xmin_sub, ymin_sub, xmax_sub, ymax_sub = bbox
        else:
            xmin_sub, ymin_sub, _, xmax_sub, ymax_sub, _ = bbox

        if not ((ymin_sub >= ymin) and (ymax_sub <= ymax)):
            raise ValueError(
                f"`BBOX` {bbox} not fully contained in `Overall BBOX` {overall_bbox}"
            )

        sub_crossing_antimeridian = xmin_sub > xmax_sub
        if not crossing_antimeridian and sub_crossing_antimeridian:
            raise ValueError(
                f"`BBOX` {bbox} not fully contained in `Overall BBOX` {overall_bbox}"
            )

        elif crossing_antimeridian:
            # TODO:
            # here we need to check for 4 cases
            # 1. sub-sequent within the right part of the overall bbox
            # 2. sub-sequent within the left part of the overall bbox
            # 3. if sub-sequent also cross the antimeridian we need to check both part with both overall part
            #
            #                               │
            #                               │
            #      [176,1,179,3]            │
            #           │                   │
            #           │                   │                               [-178,1,-176,3]
            #           │                   │
            #           │  ┌─────────────────────────────────────────┐        │
            #           │  │                │                        │        │
            #           │  │  ┌──────┐      │        ┌─────────┐     │        │
            #           └──│──►  2   │      │        │    1    │     │        │
            #              │  │      │      │        │         │◄────│────────┘
            #              │  └──────┘      │        └─────────┘     │
            #              │                │                        │
            #  ────────────│────────────────┼────────────────────────│────────────────
            #              │                │                        │
            #              │         ┌──────────────┐                │
            #              │         │      │       │                │
            #              │         │      │  3    │                │
            #              │         │      │       │◄────────┐      │◄──────────── [5,-3,-174,5]
            #              │         │      │       │         │      │
            #              │         └──────────────┘         │      │
            #              │                │                 │      │
            #              └──────────────────────────────────┼──────┘
            #                               │                 │
            #                               │                 │
            #                               │                 │
            #                               │                 │
            #                               │             [1,-2,-179,-1]
            #                               │

            pass

        else:
            if not ((xmin_sub >= xmin) and (xmax_sub <= xmax)):
                raise ValueError(
                    f"`BBOX` {bbox} not fully contained in `Overall BBOX` {overall_bbox}"
                )

    return v


def validate_time_interval(v: TInterval) -> TInterval:  # noqa: C901
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

    bbox: Annotated[List[BBox], AfterValidator(validate_bbox_interval)]


class TimeInterval(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#temporal-extent-object
    """

    interval: Annotated[TInterval, AfterValidator(validate_time_interval)]


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
