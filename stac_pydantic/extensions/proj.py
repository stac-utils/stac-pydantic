from typing import Any, Dict, Optional, Union

from geojson_pydantic.geometries import Polygon
from pydantic import BaseModel, Field

from ..shared import BBox, NumType


class CentroidObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/projection#centroid-object
    """

    lat: NumType
    lon: NumType


class ProjectionExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/projection#projection-extension-specification
    """

    epsg: Optional[Union[int]] = Field(..., alias="proj:epsg")
    proj4: Optional[Union[str]] = Field(None, alias="proj:proj4")
    wk2: Optional[Union[str, None]] = Field(None, alias="proj:wk2")
    projjson: Optional[Union[Dict[Any, Any], None]] = Field(None, alias="proj:projjson")
    geometry: Optional[Polygon] = Field(None, alias="proj:geometry")
    bbox: Optional[BBox] = Field(None, alias="proj:bbox")
    centroid: Optional[CentroidObject] = Field(None, alias="proj:centroid")

    class Config:
        allow_population_by_field_name = True
