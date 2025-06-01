from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Union

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
from typing_extensions import Annotated

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

Intersection = Union[
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    GeometryCollection,
]


class Search(BaseModel):
    """
    The base class for STAC API searches.

    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#query-parameter-table
    """

    collections: Optional[List[str]] = None
    ids: Optional[List[str]] = None
    bbox: Annotated[Optional[BBox], AfterValidator(validate_bbox)] = None
    intersects: Optional[Intersection] = None
    datetime: Annotated[Optional[str], AfterValidator(validate_datetime)] = None
    limit: Optional[int] = 10

    @property
    def start_date(self) -> Optional[dt]:
        start_date: Optional[dt] = None
        if self.datetime:
            start_date = str_to_datetimes(self.datetime)[0]
        return start_date

    @property
    def end_date(self) -> Optional[dt]:
        end_date: Optional[dt] = None
        if self.datetime:
            dates = str_to_datetimes(self.datetime)
            end_date = dates[0] if len(dates) == 1 else dates[1]
        return end_date

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @model_validator(mode="before")
    def validate_spatial(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("intersects") and values.get("bbox") is not None:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return values

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
