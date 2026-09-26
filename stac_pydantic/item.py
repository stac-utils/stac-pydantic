import sys
from typing import Any

from geojson_pydantic import Feature
from pydantic import (
    AnyUrl,
    ConfigDict,
    Field,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)

from stac_pydantic.links import Links
from stac_pydantic.shared import (
    SEMVER_REGEX,
    Asset,
    StacBaseModel,
    StacCommonMetadata,
    UtcDatetime,
)
from stac_pydantic.version import STAC_VERSION

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.1.0/item-spec/item-spec.md#properties-object
    """

    datetime: UtcDatetime | None = Field(...)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_datetime_or_start_end(self) -> Self:
        # When datetime is null, start_datetime and end_datetime must be specified
        if not self.datetime and (not self.start_datetime or not self.end_datetime):
            raise ValueError(
                "start_datetime and end_datetime must be specified when datetime is null"
            )

        return self

    @model_validator(mode="after")
    def validate_start_end(self) -> Self:
        # Using one of start_datetime or end_datetime requires the use of the other
        if (self.start_datetime and not self.end_datetime) or (
            not self.start_datetime and self.end_datetime
        ):
            raise ValueError(
                "use of start_datetime or end_datetime requires the use of the other"
            )
        return self

    @model_serializer(when_used="always", mode="wrap")
    def include_datetime_null(
        self,
        serializer: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ):
        """Custom Model serializer make sure to allways keep datetime."""
        data = serializer(self)
        start = data.get("start_datetime")
        end = data.get("end_datetime")
        if not data.get("datetime") and (start and end):
            if info.exclude_none and "datetime" not in (info.exclude or {}):
                data["datetime"] = None

        return data


class Item(Feature, StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.1.0/item-spec/item-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    stac_version: str = Field(STAC_VERSION, pattern=SEMVER_REGEX)
    properties: ItemProperties
    assets: dict[str, Asset]
    links: Links
    stac_extensions: list[AnyUrl] | None = []
    collection: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_bbox(cls, values: dict[str, Any]) -> dict[str, Any]:
        if isinstance(values, dict):
            if values.get("geometry") and values.get("bbox") is None:
                raise ValueError("bbox is required if geometry is not null")
        return values

    # https://github.com/developmentseed/geojson-pydantic/issues/147
    @model_serializer(when_used="always", mode="wrap")
    def _serialize(
        self,
        serializer: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ):
        data = serializer(self)
        for field in self.__geojson_exclude_if_none__:
            if field in data and data[field] is None:
                del data[field]

        if "geometry" not in data:
            if info.exclude_none and "geometry" not in (info.exclude or {}):
                data["geometry"] = None

        return data
