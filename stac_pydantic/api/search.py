from datetime import datetime as dt
from typing import Annotated, Any, TypeAlias

from geojson_pydantic.geometries import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from pydantic import AfterValidator, BaseModel, Field, model_validator

from stac_pydantic.api.extensions.fields import FieldsExtension
from stac_pydantic.api.extensions.query import Operator
from stac_pydantic.api.extensions.sort import SortExtension

# TODO: remove in 4.0
from stac_pydantic.shared import SearchDatetime  # noqa
from stac_pydantic.shared import (
    BBox,
    str_to_datetimes,
    validate_bbox,
    validate_datetime,
)

Intersection: TypeAlias = (
    Point
    | MultiPoint
    | LineString
    | MultiLineString
    | Polygon
    | MultiPolygon
    | GeometryCollection
)


class Search(BaseModel):
    """
    The base class for STAC API searches.

    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#query-parameter-table
    """

    collections: list[str] | None = None
    ids: list[str] | None = None
    bbox: Annotated[BBox | None, AfterValidator(validate_bbox)] = None
    intersects: Intersection | None = None
    datetime: Annotated[str | None, AfterValidator(validate_datetime)] = None
    limit: int | None = 10

    @property
    def start_date(self) -> dt | None:
        start_date: dt | None = None
        if self.datetime:
            start_date = str_to_datetimes(self.datetime)[0]
        return start_date

    @property
    def end_date(self) -> dt | None:
        end_date: dt | None = None
        if self.datetime:
            dates = str_to_datetimes(self.datetime)
            end_date = dates[0] if len(dates) == 1 else dates[1]
        return end_date

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @model_validator(mode="before")
    def validate_spatial(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("intersects") and values.get("bbox") is not None:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return values

    @property
    def spatial_filter(self) -> Intersection | None:
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

    field: FieldsExtension | None = Field(None, alias="fields")
    query: dict[str, dict[Operator, Any]] | None = None
    sortby: list[SortExtension] | None = None
