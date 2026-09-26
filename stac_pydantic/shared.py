from __future__ import annotations

from datetime import datetime as dt
from datetime import timezone
from enum import Enum, auto
from typing import Annotated, Any, Literal, cast
from warnings import warn

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
)

from stac_pydantic.utils import AutoValueEnum

NumType = float | int
BBox = (
    tuple[NumType, NumType, NumType, NumType]
    | tuple[NumType, NumType, NumType, NumType, NumType, NumType]
)

SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

# Allows for some additional flexibility in the input datetime format. As long as
# the input value has timezone information, it will be converted to UTC timezone.
UtcDatetime = Annotated[
    # Input value must be in a format which has timezone information
    AwareDatetime,
    # Convert the input value to UTC timezone
    AfterValidator(lambda d: d.astimezone(timezone.utc)),
]

SearchDatetime: TypeAdapter = TypeAdapter(UtcDatetime | None)


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
    geojsonseq = "application/geo+json-seq"
    geopackage = "application/geopackage+sqlite3"
    kml = "application/vnd.google-earth.kml+xml"
    kmz = "application/vnd.google-earth.kmz"
    pbf = "application/x-protobuf"
    mvt = "application/vnd.mapbox-vector-tile"
    # Others
    hdf = "application/x-hdf"
    hdf5 = "application/x-hdf5"
    xml = "application/xml"
    json = "application/json"
    ndjson = "application/ndjson"
    html = "text/html"
    text = "text/plain"
    openapi = "application/vnd.oai.openapi+json;version=3.0"
    openapi_yaml = "application/vnd.oai.openapi;version=3.0"
    jsonschema = "application/schema+json"
    pdf = "application/pdf"
    csv = "text/csv"
    parquet = "application/vnd.apache.parquet"
    octet_stream = "application/octet-stream"


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
    ) -> dict[str, Any]:
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

    def model_dump(  # type: ignore[override]
        self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: Any
    ) -> dict[str, Any]:
        return super().model_dump(
            by_alias=by_alias, exclude_unset=exclude_unset, **kwargs
        )

    def model_dump_json(  # type: ignore[override]
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
    description: str | None = None
    roles: list[str] | None = None
    url: str | None = None


DataType = Literal[
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float16",
    "float32",
    "float64",
    "cint16",
    "cint32",
    "cfloat32",
    "cfloat64",
    "other",
]


class Statistics(StacBaseModel):
    """STAC 1.1 common statistics for data values."""

    minimum: NumType | None = None
    maximum: NumType | None = None
    mean: NumType | None = None
    stddev: NumType | None = None
    count: int | None = Field(None, ge=0)
    valid_percent: NumType | None = Field(None, ge=0, le=100)

    model_config = ConfigDict(extra="allow")


class StacCommonMetadata(StacBaseModel):
    """Common metadata available on STAC 1.1 Items, Assets, Links, and Catalogs."""

    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    roles: list[str] | None = None
    bands: list[Band] | None = None
    data_type: DataType | None = None
    nodata: NumType | Literal["nan", "inf", "-inf"] | None = None
    statistics: Statistics | None = None
    unit: str | None = None
    datetime: UtcDatetime | None = None
    created: UtcDatetime | None = None
    updated: UtcDatetime | None = None
    start_datetime: UtcDatetime | None = None
    end_datetime: UtcDatetime | None = None
    license: str | None = None
    providers: list[Provider] | None = None
    platform: str | None = None
    instruments: list[str] | None = None
    constellation: str | None = None
    mission: str | None = None
    gsd: float | None = Field(default=None, gt=0)


class Band(StacCommonMetadata):
    """STAC 1.1 band metadata; band names are optional in the core schema."""

    name: str | None = None

    model_config = ConfigDict(extra="allow")


StacCommonMetadata.model_rebuild()
Band.model_rebuild()


class Asset(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.1.0/item-spec/item-spec.md#asset-object
    """

    href: str = Field(..., min_length=1)
    type: str | None = None

    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, extra="allow"
    )


def str_to_datetimes(value: str) -> list[dt | None]:
    # Split on "/" and replace no value or ".." with None
    values = [v if v and v != ".." else None for v in value.split("/")]

    # Cast because pylance gets confused by the type adapter and annotated type
    dates = cast(
        list[dt | None],
        [
            # Use the type adapter to validate the datetime strings, strict is necessary
            # due to pydantic issues #8736 and #8762
            SearchDatetime.validate_strings(v, strict=True) if v else None
            for v in values
        ],
    )
    return dates


def validate_datetime(v: str | None) -> str | None:
    """Validate Datetime value."""
    if v is not None:
        dates = str_to_datetimes(v)

        # If there are more than 2 dates, it's invalid
        if len(dates) > 2:
            raise ValueError(
                "Invalid datetime range. Too many values. Must match format: {begin_date}/{end_date}"
            )

        # If there is only one date, duplicate to use for both start and end dates
        if len(dates) == 1:
            dates = [dates[0], dates[0]]

        # If there is a start and end date, check that the start date is before the end date
        if dates[0] and dates[1] and dates[0] > dates[1]:
            raise ValueError(
                "Invalid datetime range. Begin date after end date. "
                "Must match format: {begin_date}/{end_date}"
            )

    return v


def validate_bbox(v: BBox | None) -> BBox | None:
    """Validate BBOX value."""
    if v:
        # Validate order
        if len(v) == 4:
            xmin, ymin, xmax, ymax = cast(tuple[int, int, int, int], v)

        elif len(v) == 6:
            xmin, ymin, min_elev, xmax, ymax, max_elev = cast(
                tuple[int, int, int, int, int, int], v
            )
            if max_elev < min_elev:
                raise ValueError(
                    "Maximum elevation must greater than minimum elevation"
                )
        else:
            raise ValueError("Bounding box must have 4 or 6 coordinates")

        # Validate against WGS84
        if xmin < -180 or ymin < -90 or xmax > 180 or ymax > 90:
            raise ValueError("Bounding box must be within (-180, -90, 180, 90)")

        if ymax < ymin:
            raise ValueError(
                f"Maximum latitude ({ymax}) must be greater than minimum latitude  ({ymin})"
            )

    return v
