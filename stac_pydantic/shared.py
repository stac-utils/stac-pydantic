from datetime import datetime as dt
from datetime import timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
from warnings import warn

import dateutil.parser
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    model_validator,
)
from typing_extensions import Annotated

from stac_pydantic.utils import AutoValueEnum

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]

SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


def datetime_to_str(d: dt) -> str:
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)

    timestamp = d.isoformat(timespec="auto")
    zulu = "+00:00"
    if timestamp.endswith(zulu):
        timestamp = f"{timestamp[: -len(zulu)]}Z"

    return timestamp


# Allows for some additional flexibility in the input datetime format.
# If the input value has timezone information, it will be converted to UTC timezone.
# Otherwise URT timezone will be assumed.
UtcDatetime = Annotated[
    Union[str, dt],
    # Input value must be in a format which has timezone information
    AfterValidator(lambda d: d if isinstance(d, dt) else dateutil.parser.isoparse(d)),
    # Use `isoformat` to serialize the value in an RFC3339 compatible format
    PlainSerializer(lambda d: datetime_to_str(d)),
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

    name: str = Field(..., alias="name", min_length=1)
    description: Optional[str] = None
    roles: Optional[List[str]] = None
    url: Optional[str] = None


class StacCommonMetadata(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/common-metadata.md#date-and-time-range
    """

    title: Optional[str] = None
    description: Optional[str] = None
    datetime: Optional[UtcDatetime] = None
    start_datetime: Optional[UtcDatetime] = None
    end_datetime: Optional[UtcDatetime] = None
    created: Optional[UtcDatetime] = None
    updated: Optional[UtcDatetime] = None
    platform: Optional[str] = None
    instruments: Optional[List[str]] = None
    constellation: Optional[str] = None
    mission: Optional[str] = None
    providers: Optional[List[Provider]] = None
    gsd: Optional[Annotated[float, Field(gt=0)]] = None

    @model_validator(mode="before")
    @classmethod
    def validate_start_end_datetime(cls, data: Any) -> Any:
        if isinstance(data, dict):

            start_datetime = data.get("start_datetime")
            end_datetime = data.get("end_datetime")

            if not all([start_datetime, end_datetime]) and any(
                [start_datetime, end_datetime]
            ):
                raise ValueError(
                    "start_datetime and end_datetime must be specified together"
                )
        return data


class Asset(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#asset-object
    """

    href: str = Field(..., alias="href", min_length=1)
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[List[str]] = None
    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, extra="allow"
    )
