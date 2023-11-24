from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Union

from geojson_pydantic import Feature
from pydantic import (
    AnyUrl,
    ConfigDict,
    Field,
    field_serializer,
    model_serializer,
    model_validator,
)

from stac_pydantic.links import Links
from stac_pydantic.shared import (
    DATETIME_RFC339,
    SEMVER_REGEX,
    Asset,
    StacBaseModel,
    StacCommonMetadata,
)
from stac_pydantic.utils import parse_datetime
from stac_pydantic.version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#properties-object
    """

    datetime: Union[dt, str] = Field(..., alias="datetime")

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def validate_datetime(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        datetime = data.get("datetime")
        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")

        if not datetime or datetime == "null":
            if not start_datetime and not end_datetime:
                raise ValueError(
                    "start_datetime and end_datetime must be specified when datetime is null"
                )

        if isinstance(datetime, str):
            data["datetime"] = parse_datetime(datetime)

        if isinstance(start_datetime, str):
            data["start_datetime"] = parse_datetime(start_datetime)

        if isinstance(end_datetime, str):
            data["end_datetime"] = parse_datetime(end_datetime)

        return data

    @field_serializer("datetime")
    def serialize_datetime(self, v: dt, _info: Any) -> str:
        return v.strftime(DATETIME_RFC339)


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
