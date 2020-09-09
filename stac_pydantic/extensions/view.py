from typing import Optional

from pydantic import BaseModel, Field

from ..shared import NumType


class ViewExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/view#item-fields
    """

    off_nadir: Optional[NumType] = Field(None, alias="view:off_nadir")
    incidence_angle: Optional[NumType] = Field(None, alias="view:incidence_angle")
    azimuth: Optional[NumType] = Field(None, alias="view:azimuth")
    sun_azimuth: Optional[NumType] = Field(None, alias="view:sun_azimuth")
    sun_elevation: Optional[NumType] = Field(None, alias="view:sun_elevation")

    class Config:
        allow_population_by_field_name = True
