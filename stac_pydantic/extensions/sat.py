from enum import auto
from typing import List, Optional

from pydantic import BaseModel, Field

from ..utils import AutoValueEnum


class OrbitStates(str, AutoValueEnum):
    ascending = auto()
    descending = auto()
    geostationary = auto()


class SatelliteExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    orbit_state: Optional[OrbitStates]
    relative_orbit: Optional[str]
    platform: Optional[str] = Field(None, alias="platform")
    instruments: Optional[List[str]] = Field(None, alias="instruments")
    constellation: Optional[str] = Field(None, alias="constellation")
    mission: Optional[str] = Field(None, alias="mission")

    class Config:
        use_enum_values = True
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"sat:{field_name}"
