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

from stac_pydantic.api.extensions.fields import FieldsExtension
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.api.extensions.sort import SortExtension
from stac_pydantic.shared import DATETIME_RFC339, BBox


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

    @property
    def start_date(self) -> Optional[datetime]:
        values = self.datetime.split("/")
        if len(values) == 1:
            return None
        if values[0] == "..":
            return None
        return datetime.strptime(values[0], DATETIME_RFC339)

    @property
    def end_date(self) -> Optional[datetime]:
        values = self.datetime.split("/")
        if len(values) == 1:
            return datetime.strptime(values[0], DATETIME_RFC339)
        if values[1] == "..":
            return None
        return datetime.strptime(values[1], DATETIME_RFC339)

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
        return v
