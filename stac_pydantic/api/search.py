from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from geojson_pydantic.geometries import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from pydantic import BaseModel, Field, validator

from ..shared import DATETIME_RFC339, BBox
from .extensions.fields import FieldsExtension
from .extensions.query import Operator
from .extensions.sort import SortExtension


class Search(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#filter-parameters-and-fields
    """

    collections: List[str]
    ids: Optional[List[str]]
    bbox: Optional[BBox]
    intersects: Optional[
        Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]
    ]
    datetime: Optional[str]
    limit: int = 10
    field: Optional[FieldsExtension] = Field(None, alias="fields")
    query: Optional[Dict[str, Dict[Operator, Any]]]
    sortby: Optional[List[SortExtension]]

    @validator("intersects")
    def validate_spatial(cls, v, values):
        if v and values["bbox"]:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return v

    @validator("datetime")
    def validate_datetime(cls, v):
        if "/" in v:
            values = v.split("/")
        else:
            # Single date is interpreted as end date
            values = ["..", v]

        dates = []
        for value in values:
            if value == "..":
                dates.append(value)
                continue
            try:
                datetime.strptime(value, DATETIME_RFC339)
                dates.append(value)
            except:
                raise ValueError(
                    f"Invalid datetime, must match format ({DATETIME_RFC339})."
                )

        if ".." not in dates:
            if datetime.strptime(dates[0], DATETIME_RFC339) > datetime.strptime(
                dates[1], DATETIME_RFC339
            ):
                raise ValueError(
                    "Invalid datetime range, must match format (begin_date, end_date)"
                )

        return dates
