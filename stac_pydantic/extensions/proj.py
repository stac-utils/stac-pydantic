from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from ..geojson import Polygon
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

    epsg: Optional[Union[int]] = ...
    proj4: Optional[Union[str]]
    wk2: Optional[Union[str, None]]
    projjson: Optional[Union[Dict[Any, Any], None]]
    geometry: Optional[Polygon]
    bbox: Optional[BBox]
    centroid: Optional[CentroidObject]

    class Config:
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"proj:{field_name}"
