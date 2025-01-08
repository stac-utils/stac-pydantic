from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from geojson_pydantic.geometries import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from pydantic import BaseModel, Field, TypeAdapter, field_validator, model_validator

from stac_pydantic.api.extensions.fields import FieldsExtension
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.api.extensions.sort import SortExtension
from stac_pydantic.shared import BBox, UtcDatetime

Intersection = Union[
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    GeometryCollection,
]

SearchDatetime = TypeAdapter(Optional[UtcDatetime])


class Search(BaseModel):
    """
    The base class for STAC API searches.

    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#query-parameter-table
    """

    collections: Optional[List[str]] = None
    ids: Optional[List[str]] = None
    bbox: Optional[BBox] = None
    intersects: Optional[Intersection] = None
    datetime: Optional[str] = None
    limit: Optional[int] = 10

    # Private properties to store the parsed datetime values. Not part of the model schema.
    _start_date: Optional[dt] = None
    _end_date: Optional[dt] = None

    # Properties to return the private values
    @property
    def start_date(self) -> Optional[dt]:
        return self._start_date

    @property
    def end_date(self) -> Optional[dt]:
        return self._end_date

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @model_validator(mode="before")
    def validate_spatial(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("intersects") and values.get("bbox") is not None:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return values

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: BBox) -> BBox:
        if v:
            # Validate order
            if len(v) == 4:
                xmin, ymin, xmax, ymax = cast(Tuple[int, int, int, int], v)
            else:
                xmin, ymin, min_elev, xmax, ymax, max_elev = cast(
                    Tuple[int, int, int, int, int, int], v
                )
                if max_elev < min_elev:
                    raise ValueError(
                        "Maximum elevation must greater than minimum elevation"
                    )

            if xmax < xmin:
                raise ValueError(
                    "Maximum longitude must be greater than minimum longitude"
                )

            if ymax < ymin:
                raise ValueError(
                    "Maximum longitude must be greater than minimum longitude"
                )

            # Validate against WGS84
            if xmin < -180 or ymin < -90 or xmax > 180 or ymax > 90:
                raise ValueError("Bounding box must be within (-180, -90, 180, 90)")

        return v

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, value: Optional[str]) -> Optional[str]:
        # Split on "/" and replace no value or ".." with None
        if value is None:
            return value
        values = [v if v and v != ".." else None for v in value.split("/")]

        # If there are more than 2 dates, it's invalid
        if len(values) > 2:
            raise ValueError(
                "Invalid datetime range. Too many values. Must match format: {begin_date}/{end_date}"
            )

        # If there is only one date, duplicate to use for both start and end dates
        if len(values) == 1:
            values = [values[0], values[0]]

        # Cast because pylance gets confused by the type adapter and annotated type
        dates = cast(
            List[Optional[dt]],
            [
                # Use the type adapter to validate the datetime strings, strict is necessary
                # due to pydantic issues #8736 and #8762
                SearchDatetime.validate_strings(v, strict=True) if v else None
                for v in values
            ],
        )

        # If there is a start and end date, check that the start date is before the end date
        if dates[0] and dates[1] and dates[0] > dates[1]:
            raise ValueError(
                "Invalid datetime range. Begin date after end date. "
                "Must match format: {begin_date}/{end_date}"
            )

        # Store the parsed dates
        cls._start_date = dates[0]
        cls._end_date = dates[1]
        # Return the original string value
        return value

    @property
    def spatial_filter(self) -> Optional[Intersection]:
        """Return a geojson-pydantic object representing the spatial filter for the search request.

        Check for both because the ``bbox`` and ``intersects`` parameters are mutually exclusive.
        """
        if self.bbox:
            return Polygon.from_bounds(*self.bbox)
        if self.intersects:
            return self.intersects
        else:
            return None


class ExtendedSearch(Search):
    """
    STAC API search with extensions enabled.
    """

    field: Optional[FieldsExtension] = Field(None, alias="fields")
    query: Optional[Dict[str, Dict[Operator, Any]]] = None
    sortby: Optional[List[SortExtension]] = None
