from datetime import datetime
from typing import List, Optional, Union

from geojson_pydantic.geometries import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from pydantic import BaseModel, Field, root_validator

from .extensions.fields import FieldsExtension
from ..shared import BBox


class Search(BaseModel):
    collections: List[str]
    ids: Optional[List[str]]
    bbox: Optional[BBox]
    intersects: Optional[Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]]
    datetime: Optional[Union[str, datetime]]
    limit: int = 10
    field: Optional[FieldsExtension] = Field(None, alias="fields")

    @root_validator
    def validate_spatial_query(cls, values):
        # Validate geometry params
        if values['intersects'] and values['bbox']:
            raise ValueError("intersects and bbox parameters are mutually exclusive")
        return values