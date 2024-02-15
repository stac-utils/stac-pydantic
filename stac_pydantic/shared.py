from datetime import datetime as dt
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
from warnings import warn

from ciso8601 import parse_rfc3339
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from stac_pydantic.utils import AutoValueEnum

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]

SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

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

    title: Optional[str] = Field(None, alias="title")
    description: Optional[str] = Field(None, alias="description")
    datetime: Optional[dt] = Field(None, alias="datetime")
    start_datetime: Optional[dt] = Field(None, alias="start_datetime")
    end_datetime: Optional[dt] = Field(None, alias="end_datetime")
    created: Optional[dt] = Field(None, alias="created")
    updated: Optional[dt] = Field(None, alias="updated")
    license: Optional[str] = Field(None, alias="license")
    platform: Optional[str] = Field(None, alias="platform")
    instruments: Optional[List[str]] = Field(None, alias="instruments")
    constellation: Optional[str] = Field(None, alias="constellation")
    mission: Optional[str] = Field(None, alias="mission")
    providers: Optional[List[Provider]] = Field(None, alias="providers")
    gsd: Optional[float] = Field(None, alias="gsd", gt=0)

    @model_validator(mode="before")
    @classmethod
    def validate_start_end_datetime(cls, data: Any) -> Any:
        if isinstance(data, dict):

            start_datetime = data.get("start_datetime")
            end_datetime = data.get("end_datetime")
            datetime = data.get("datetime")
            created = data.get("created")
            updated = data.get("updated")

            if not all([start_datetime, end_datetime]) and any(
                [start_datetime, end_datetime]
            ):
                raise ValueError(
                    "start_datetime and end_datetime must be specified together"
                )

            if isinstance(datetime, str):
                data["datetime"] = parse_rfc3339(datetime)

            if isinstance(start_datetime, str):
                data["start_datetime"] = parse_rfc3339(start_datetime)

            if isinstance(end_datetime, str):
                data["end_datetime"] = parse_rfc3339(end_datetime)

            if isinstance(created, str):
                data["created"] = parse_rfc3339(created)

            if isinstance(updated, str):
                data["updated"] = parse_rfc3339(updated)

        return data

    @field_serializer(
        "datetime", "start_datetime", "end_datetime", "created", "updated"
    )
    def serialize_datetime(self, v: dt, _info: Any) -> str:
        if v is None:
            return None
        else:
            return v.strftime(DATETIME_RFC339)


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
