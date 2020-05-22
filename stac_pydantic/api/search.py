from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from geojson_pydantic.geometries import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from pydantic import BaseModel, Field, root_validator

from .extensions.fields import FieldsExtension
from .extensions.query import Operator
from .extensions.sort import SortExtension
from ..shared import BBox


class Search(BaseModel):
    collections: List[str]
    ids: Optional[List[str]]
    bbox: Optional[BBox]
    intersects: Optional[Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]]
    datetime: Optional[Union[str, datetime]]
    limit: int = 10
    field: Optional[FieldsExtension] = Field(None, alias="fields")
    query: Optional[Dict[str, Dict[Operator, Any]]]
    sortby: Optional[List[SortExtension]]

    @root_validator
    def validate_spatial_query(cls, values):
        # Validate geometry params
        if values['intersects'] and values['bbox']:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return values