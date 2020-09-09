from enum import auto
from typing import List, Optional

from pydantic import BaseModel, Field

from ..utils import AutoValueEnum


class CommonBandNames(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/eo#common-band-names
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
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/eo#band-object
    """

    name: Optional[str]
    common_name: Optional[CommonBandNames]
    center_wavelength: Optional[float]
    full_width_half_max: Optional[float]
    description: Optional[str]


class ElectroOpticalExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/eo#electro-optical-extension-specification
    """

    bands: Optional[List[BandObject]] = Field(None, alias="eo:bands")
    cloud_cover: Optional[float] = Field(None, alias="eo:cloud_cover")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
