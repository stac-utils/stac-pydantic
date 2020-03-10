from typing import Optional

from pydantic import BaseModel

from ..shared import NumType


class ViewExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/view#view-geometry-extension-specification
    """

    off_nadir: Optional[NumType]
    incidence_angle: Optional[NumType]
    azimuth: Optional[NumType]
    sun_azimuth: Optional[NumType]
    sun_elevation: Optional[NumType]

    class Config:
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"view:{field_name}"
