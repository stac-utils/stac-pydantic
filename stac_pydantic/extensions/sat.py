from enum import auto
from typing import Optional

from pydantic import BaseModel, Field

from stac_pydantic.utils import AutoValueEnum


class OrbitStates(str, AutoValueEnum):
    """
    https://github.com/stac-extensions/sat#satorbit_state
    """

    ascending = auto()
    descending = auto()
    geostationary = auto()


class SatelliteExtension(BaseModel):
    """
    https://github.com/stac-extensions/sat
    """

    orbit_state: Optional[OrbitStates] = Field(None, alias="sat:orbit_state")
    relative_orbit: Optional[int] = Field(None, alias="sat:relative_orbit")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
