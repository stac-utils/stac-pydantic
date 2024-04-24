from typing import Any, Dict, List, Optional

from geojson_pydantic import Feature
from pydantic import AnyUrl, ConfigDict, Field, model_serializer, model_validator
from typing_extensions import Self

from stac_pydantic.links import Links
from stac_pydantic.shared import (
    SEMVER_REGEX,
    Asset,
    StacBaseModel,
    StacCommonMetadata,
    UtcDatetime,
)
from stac_pydantic.version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#properties-object
    """

    datetime: Optional[UtcDatetime]

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_datetime(self) -> Self:
        if not self.datetime and (not self.start_datetime or not self.end_datetime):
            raise ValueError(
                "start_datetime and end_datetime must be specified when datetime is null"
            )

        return self


class Item(Feature, StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    stac_version: str = Field(STAC_VERSION, pattern=SEMVER_REGEX)
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = []
    collection: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_bbox(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values, dict):
            if values.get("geometry") and values.get("bbox") is None:
                raise ValueError("bbox is required if geometry is not null")
        return values

    # https://github.com/developmentseed/geojson-pydantic/issues/147
    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        for field in self.__geojson_exclude_if_none__:
            if field in data and data[field] is None:
                del data[field]
        return data
