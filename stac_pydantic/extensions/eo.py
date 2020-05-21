from enum import auto
from typing import List, Optional

from pydantic import BaseModel

from ..shared import NumType
from ..utils import AutoValueEnum


class CommonBandNames(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/eo#common-band-names
    """

    coastal = auto()
    blue = auto()
    green = auto()
    red = auto()
    yellow = auto()
    pan = auto()
    rededge = auto()
    nir = auto()
    nir08 = auto()
    nir09 = auto()
    cirrus = auto()
    swir16 = auto()
    swir22 = auto()
    lwir = auto()
    lwir11 = auto()
    lwir12 = auto()


class BandObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/eo#band-object
    """

    name: Optional[str]
    common_name: Optional[CommonBandNames]
    center_wavelength: Optional[NumType]
    full_width_half_max: Optional[NumType]
    description: Optional[str]


class ElectroOpticalExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/eo#electro-optical-extension-specification
    """

    gsd: NumType
    bands: List[BandObject]
    cloud_cover: Optional[NumType]

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        alias_generator = lambda field_name: f"eo:{field_name}"
