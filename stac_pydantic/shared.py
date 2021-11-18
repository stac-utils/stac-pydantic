from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel, Extra, Field, confloat, constr

from stac_pydantic.utils import AutoValueEnum

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]

# https://tools.ietf.org/html/rfc3339#section-5.6
# Unused, but leaving it here since it's used by dependencies
DATETIME_RFC339 = "%Y-%m-%dT%H:%M:%SZ"


class MimeTypes(str, Enum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#media-types
    """

    # Raster
    geotiff = "image/tiff; application=geotiff"
    cog = "image/tiff; application=geotiff; profile=cloud-optimized"
    jp2 = "image/jp2"
    png = "image/png"
    jpeg = "image/jpeg"
    # Vector
    geojson = "application/geo+json"
    geopackage = "application/geopackage+sqlite3"
    kml = "application/vnd.google-earth.kml+xml"
    kmz = "application/vnd.google-earth.kmz"
    # Others
    hdf = "application/x-hdf"
    hdf5 = "application/x-hdf5"
    xml = "application/xml"
    json = "application/json"
    html = "text/html"
    text = "text/plain"
    openapi = "application/vnd.oai.openapi+json;version=3.0"


class AssetRoles(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/extensions/asset/README.md
    """

    thumbnail = auto()
    overview = auto()
    data = auto()
    metadata = auto()


class ProviderRoles(str, AutoValueEnum):
    licensor = auto()
    producer = auto()
    processor = auto()
    host = auto()


class Provider(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#provider-object
    """

    name: constr(min_length=1)
    description: Optional[str]
    roles: Optional[List[str]]
    url: Optional[str]


class StacCommonMetadata(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/common-metadata.md#date-and-time-range
    """

    title: Optional[str] = Field(None, alias="title")
    description: Optional[str] = Field(None, alias="description")
    start_datetime: Optional[datetime] = Field(None, alias="start_datetime")
    end_datetime: Optional[datetime] = Field(None, alias="end_datetime")
    created: Optional[datetime] = Field(None, alias="created")
    updated: Optional[datetime] = Field(None, alias="updated")
    platform: Optional[str] = Field(None, alias="platform")
    instruments: Optional[List[str]] = Field(None, alias="instruments")
    constellation: Optional[str] = Field(None, alias="constellation")
    mission: Optional[str] = Field(None, alias="mission")
    providers: Optional[List[Provider]] = Field(None, alias="providers")
    gsd: Optional[confloat(gt=0)] = Field(None, alias="gsd")

    class Config:
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_RFC339)}


class Asset(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#asset-object
    """

    href: constr(min_length=1)
    type: Optional[str]
    title: Optional[str]
    description: Optional[str]
    roles: Optional[List[str]]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        extra = Extra.allow
