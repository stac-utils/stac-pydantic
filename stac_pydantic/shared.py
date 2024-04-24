from datetime import timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
from warnings import warn

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
)
from typing_extensions import Annotated

from stac_pydantic.utils import AutoValueEnum

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]

SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

# Allows for some additional flexibility in the input datetime format. As long as
# the input value has timezone information, it will be converted to UTC timezone.
UtcDatetime = Annotated[
    # Input value must be in a format which has timezone information
    AwareDatetime,
    # Convert the input value to UTC timezone
    AfterValidator(lambda d: d.astimezone(timezone.utc)),
    # Use `isoformat` to serialize the value in an RFC3339 compatible format
    # for example: "2024-01-01T00:00:00+00:00"
    PlainSerializer(lambda d: d.isoformat()),
]


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
    jsonschema = "application/schema+json"


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


class StacBaseModel(BaseModel):
    def to_dict(
        self, by_alias: bool = True, exclude_unset: bool = True, **kwargs: Any
    ) -> Dict[str, Any]:
        warn(
            "`to_dict` method is deprecated. Use `model_dump` instead",
            DeprecationWarning,
        )
        return self.model_dump(by_alias=by_alias, exclude_unset=exclude_unset, **kwargs)

    def to_json(
        self, by_alias: bool = True, exclude_unset: bool = True, **kwargs: Any
    ) -> str:
        warn(
            "`to_json` method is deprecated. Use `model_dump_json` instead",
            DeprecationWarning,
        )
        return self.model_dump_json(
            by_alias=by_alias, exclude_unset=exclude_unset, **kwargs
        )

    def model_dump(
        self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: Any
    ) -> Dict[str, Any]:
        return super().model_dump(
            by_alias=by_alias, exclude_unset=exclude_unset, **kwargs
        )

    def model_dump_json(
        self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: Any
    ) -> str:
        return super().model_dump_json(
            by_alias=by_alias, exclude_unset=exclude_unset, **kwargs
        )


class Provider(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#provider-object
    """

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    roles: Optional[List[str]] = None
    url: Optional[str] = None


class StacCommonMetadata(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/common-metadata.md#date-and-time-range
    """

    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[UtcDatetime] = None
    end_datetime: Optional[UtcDatetime] = None
    created: Optional[UtcDatetime] = None
    updated: Optional[UtcDatetime] = None
    platform: Optional[str] = None
    instruments: Optional[List[str]] = None
    constellation: Optional[str] = None
    mission: Optional[str] = None
    providers: Optional[List[Provider]] = None
    gsd: Optional[float] = Field(None, gt=0)


class Asset(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#asset-object
    """

    href: str = Field(..., min_length=1)
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[List[str]] = None

    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, extra="allow"
    )
