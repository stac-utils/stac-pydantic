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


def validate_bbox_interval(v: List[BBox]) -> List[BBox]:  # noqa: C901
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
        error_msg = ValueError(
            f"`BBOX` {bbox} not fully contained in `Overall BBOX` {overall_bbox}"
        )
        _ = validate_bbox(bbox)

        if len(bbox) == 4:
            xmin_sub, ymin_sub, xmax_sub, ymax_sub = bbox
        else:
            xmin_sub, ymin_sub, _, xmax_sub, ymax_sub, _ = bbox

        if not ((ymin_sub >= ymin) and (ymax_sub <= ymax)):
            raise error_msg

        sub_crossing_antimeridian = xmin_sub > xmax_sub
        if not crossing_antimeridian and sub_crossing_antimeridian:
            raise error_msg

        elif crossing_antimeridian:
            #                           Antimeridian
            #     0                     + 180 │ - 180                            0
            #     │  [176,1,179,3]            │                                  │
            #     │       │                   │                                  │
            #     │       │                   │                                  │
            #     │       │                   │                                  │     [-178,1,-176,3]
            #     │       │  ┌─────────────────────────────────────────┐         │           │
            #     │       │  │       xmax_sub │               xmax_sub │         │           │
            #     │       │  │  ┌──────|      │        ┌─────────|     │         │           │
            #     │       └──│──►  2   │      │        │    3    │     │         │           │
            #     |          │  │      │      │        │         │◄────│─────────┼───────────┘
            #     │          │  |──────┘      │        |─────────┘     │         │
            #     │          │xmin_sub        │    xmin_sub            │         │         0
            #   ──┼──────────│────────────────┼────────────────────────│─────────┼──────────
            #     │          │                │    xmax_sub(-179)      │         │
            #     │          │         ┌──────────────|                │         │
            #     │          │         │      │       │                │         │
            #     │          │         │      │  1    │                │         │
            #     |          │         │      │       │◄────────┐      │◄────────┼─────── [175,-3,-174,5]
            #     │          │         │      │       │         │      │         │
            #     │          │         |──────────────┘         │      │         │
            #     │          │   xmin_sub(179)│                 │      │         │
            #     │          |──────────────────────────────────┼──────|         │
            #     │      xmin(174)            │                 │ xmax(-174)     │
            #     │                           │                 │                │
            #     │                           │                 │                │
            #     │                           │                 │                │
            #     │                           │          [179,-2,-179,-1]        │

            # Case 1
            if sub_crossing_antimeridian:
                if not (xmin_sub > xmin and xmax_sub < xmax):
                    raise error_msg

            # Case 2: if sub-sequent has lon > 0 (0 -> 180 side), then we must check if
            # its min lon is < to the western lon (xmin for bbox crossing antimeridian limit)
            # of the overall bbox (on 0 -> +180 side)
            elif xmin_sub >= 0 and xmin_sub < xmin:
                raise error_msg

            # Case 3: if sub-sequent has lon < 0 (-180 -> 0 side), then we must check if
            # its max lon is > to the eastern lon (xmax for bbox crossing antimeridian limit)
            #  of the overall bbox (on -180 -> 0 side)
            elif xmin_sub <= 0 and xmax_sub > xmax:
                raise error_msg

        else:
            if not ((xmin_sub >= xmin) and (xmax_sub <= xmax)):
                raise error_msg

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
