from enum import auto
from typing import List, Optional

from pydantic import BaseModel, Field

from ..shared import NumType
from ..utils import AutoValueEnum


class PolarizationEnum(str, AutoValueEnum):
    HH = auto()
    VV = auto()
    HV = auto()
    VH = auto()


class Polarizations(BaseModel):
    __root__: List[PolarizationEnum]

    def __getitem__(self, item):
        return self.__root__[item].value


class FrequencyBands(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/sar#common-frequency-band-names
    """

    P = auto()
    L = auto()
    S = auto()
    C = auto()
    X = auto()
    Ku = auto()
    K = auto()
    Ka = auto()


class ObservationDirections(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/sar#item-fields
    """

    left = auto()
    right = auto()


class SARExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/sar#sar-extension-specification
    """

    instrument_mode: str = Field(..., alias="sar:instrument_mode")
    center_frequency: Optional[NumType] = Field(None, alias="sar:center_frequency")
    polarizations: Polarizations = Field(..., alias="sar:polarizations")
    product_type: str = Field(..., alias="sar:product_type")
    resolution_range: Optional[int] = Field(None, alias="sar:resolution_range")
    resolution_azimuth: Optional[int] = Field(None, alias="sar:resolution_azimuth")
    pixel_spacing_range: Optional[int] = Field(None, alias="sar:pixel_spacing_range")
    pixel_spacing_azimuth: Optional[int] = Field(
        None, alias="sar:pixel_spacing_azimuth"
    )
    looks_range: Optional[int] = Field(None, alias="sar:look_range")
    looks_azimuth: Optional[NumType] = Field(None, alias="sar:looks_azimuth")
    looks_equivalent_number: Optional[NumType] = Field(
        None, alias="sar:looks_equivalent_number"
    )
    observation_direction: Optional[ObservationDirections] = Field(
        None, alias="sar:observation_direction"
    )
    frequency_band: FrequencyBands = Field(..., alias="sar:frequency_band")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
