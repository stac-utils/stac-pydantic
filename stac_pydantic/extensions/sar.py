from enum import auto
from typing import List, Optional

from pydantic import BaseModel

from ..shared import NumType
from ..utils import AutoValueEnum


class Polarizations(str, AutoValueEnum):
    HH = auto()
    VV = auto()
    HV = auto()
    VH = auto()


class FrequencyBands(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    P = auto()
    L = auto()
    S = auto()
    C = auto()
    X = auto()
    Ku = auto()
    K = auto()
    Ka = auto()


class SARExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    instrument_mode: str
    frequency_band: FrequencyBands
    center_frequency: Optional[NumType]
    polarizations: List[Polarizations]
    product_type: str
    resolution_range: Optional[int]
    resolution_azimuth: Optional[int]
    pixel_spacing_range: Optional[int]
    pixel_spacing_azimuth: Optional[int]
    looks_range: Optional[int]
    looks_equivalent_number: Optional[int]
    observation_direction: Optional[str]

    class Config:
        use_enum_values = True
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"sar:{field_name}"
