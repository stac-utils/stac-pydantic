from enum import auto
from typing import Optional

from pydantic import BaseModel, Field

from ..utils import AutoValueEnum


class OrbitStates(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/sat#item-fields
    """

    ascending = auto()
    descending = auto()
    geostationary = auto()


class SatelliteExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/sat#satellite-extension-specification
    """

    orbit_state: Optional[OrbitStates] = Field(None, alias="sat:orbit_state")
    relative_orbit: Optional[int] = Field(None, alias="sat:relative_orbit")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
