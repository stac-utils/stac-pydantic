from typing import Any, Dict, List, Optional, Union

from geojson_pydantic.geometries import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from pydantic import BaseModel, Field

from stac_pydantic.shared import BBox, NumType


class CentroidObject(BaseModel):
    """
    https://github.com/stac-extensions/projection#centroid-object
    """

    lat: NumType
    lon: NumType


class ProjectionExtension(BaseModel):
    """
    https://github.com/stac-extensions/projection
    """

    epsg: Optional[Union[int]] = Field(..., alias="proj:epsg")
    wk2: Optional[Union[str, None]] = Field(None, alias="proj:wk2")
    projjson: Optional[Union[Dict[Any, Any], None]] = Field(None, alias="proj:projjson")
    geometry: Optional[
        Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]
    ] = Field(None, alias="proj:geometry")
    bbox: Optional[BBox] = Field(None, alias="proj:bbox")
    centroid: Optional[CentroidObject] = Field(None, alias="proj:centroid")
    shape: Optional[List[int]] = Field(None, alias="proj:shape")
    transform: Optional[List[float]] = Field(None, alias="proj:transform")

    class Config:
        allow_population_by_field_name = True
