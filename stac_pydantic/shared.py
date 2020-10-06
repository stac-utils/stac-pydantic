from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel, Extra, Field

from .extensions.eo import BandObject
from .utils import AutoValueEnum

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]

# https://tools.ietf.org/html/rfc3339#section-5.6
DATETIME_RFC339 = "%Y-%m-%dT%H:%M:%SZ"


class ExtensionTypes(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/extensions/README.md#list-of-content-extensions
    """

    asset = auto()
    checksum = auto()
    collection_assets = "collection-assets"
    context = auto()
    cube = auto()
    eo = auto()
    item_assets = "item-assets"
    label = auto()
    pc = auto()
    projection = auto()
    sar = auto()
    sat = auto()
    sci = auto()
    single_file_stac = "single-file-stac"
    version = auto()
    view = auto()


class MimeTypes(str, Enum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/item-spec.md#media-types
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


class Relations(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#relation-types
    """

    self = auto()
    root = auto()
    parent = auto()
    child = auto()
    item = auto()
    license = auto()
    derived_from = auto()
    collection = auto()
    alternate = auto()
    previous = auto()
    next = auto()
    conformance = auto()
    docs = auto()
    tiles = auto()
    search = auto()


class AssetRoles(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/extensions/asset/README.md
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


class Link(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#link-object
    """

    href: str
    rel: str
    type: Optional[str]
    title: Optional[str]
    # Label extension
    label: Optional[str] = Field(None, alias="label:assets")

    class Config:
        use_enum_values = True


class Provider(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#provider-object
    """

    name: str
    description: Optional[str]
    roles: Optional[List[str]]
    url: Optional[str]


class StacCommonMetadata(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/common-metadata.md#date-and-time-range
    """

    title: Optional[str] = Field(None, alias="title")
    description: Optional[str] = Field(None, alias="description")
    start_datetime: Optional[Union[str, datetime]] = Field(None, alias="start_datetime")
    end_datetime: Optional[Union[str, datetime]] = Field(None, alias="end_datetime")
    created: Optional[Union[str, datetime]] = Field(None, alias="created")
    updated: Optional[Union[str, datetime]] = Field(None, alias="updated")
    platform: Optional[str] = Field(None, alias="platform")
    instruments: Optional[List[str]] = Field(None, alias="instruments")
    constellation: Optional[str] = Field(None, alias="constellation")
    mission: Optional[str] = Field(None, alias="mission")
    providers: Optional[List[Provider]] = Field(None, alias="providers")
    gsd: Optional[NumType] = Field(None, alias="gsd")


class Asset(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/item-spec/item-spec.md#asset-object
    """

    href: str
    type: Optional[str]
    title: Optional[str]
    description: Optional[str]
    roles: Optional[List[AssetRoles]]
    # EO extension
    bands: Optional[List[BandObject]] = Field(None, alias="eo:bands")
    # SAR extension
    polarizations: Optional[List[str]] = Field(None, alias="sar:polarizations")
    # Checksum extension
    multihash: Optional[str] = Field(None, alias="checksum:multihash")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        extra = Extra.allow
