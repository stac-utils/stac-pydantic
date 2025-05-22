from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union

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


def _normalize_bounds(
    xmin: NumType, ymin: NumType, xmax: NumType, ymax: NumType
) -> Tuple[NumType, NumType, NumType, NumType]:
    """Return BBox in correct minx, miny, maxx, maxy order."""
    return (
        min(xmin, xmax),
        min(ymin, ymax),
        max(xmin, xmax),
        max(ymin, ymax),
    )


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

    # if bbox is crossing the Antimeridian limit we move xmax to the west
    if xmin > xmax:
        xmax = 180 - (xmax % 360)

    xmin, ymin, xmax, ymax = _normalize_bounds(xmin, ymin, xmax, ymax)
    for bbox in ivalues:
        _ = validate_bbox(bbox)

        if len(bbox) == 4:
            xminb, yminb, xmaxb, ymaxb = bbox
        else:
            xminb, yminb, _, xmaxb, ymaxb, _ = bbox

        if xminb > xmaxb:
            xmaxb = 180 - (xmaxb % 360)

        xminb, yminb, xmaxb, ymaxb = _normalize_bounds(xminb, yminb, xmaxb, ymaxb)
        if not (
            (xminb >= xmin) and (xmaxb <= xmax) and (yminb >= ymin) and (ymaxb <= ymax)
        ):
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
