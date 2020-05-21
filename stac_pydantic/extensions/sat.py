from enum import auto
from typing import List, Optional

from pydantic import BaseModel, Field

from ..utils import AutoValueEnum


class OrbitStates(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/sat#item-fields
    """

    ascending = auto()
    descending = auto()
    geostationary = auto()


class SatelliteExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/sat#satellite-extension-specification
    """

    orbit_state: Optional[OrbitStates] = Field(None, alias="sat:orbite_state")
    relative_orbit: Optional[int] = Field(None, alias="sat:relative_orbit")
    platform: Optional[str]
    instruments: Optional[List[str]]
    constellation: Optional[str]
    mission: Optional[str]

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
