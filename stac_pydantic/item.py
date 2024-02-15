from typing import Any, Dict, List, Optional

from geojson_pydantic import Feature
from pydantic import AnyUrl, ConfigDict, Field, model_serializer, model_validator

from stac_pydantic.links import Links
from stac_pydantic.shared import SEMVER_REGEX, Asset, StacBaseModel, StacCommonMetadata
from stac_pydantic.version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#properties-object
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#datetime
    """

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def validate_datetime(cls, data: Any) -> Any:
        if isinstance(data, dict):

            datetime = data.get("datetime")
            start_datetime = data.get("start_datetime")
            end_datetime = data.get("end_datetime")

            if datetime is None or datetime == "null":
                if not start_datetime and not end_datetime:
                    raise ValueError(
                        "start_datetime and end_datetime must be specified when datetime is null"
                    )
                data["datetime"] = None

        return data


class Item(Feature, StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    stac_version: str = Field(..., pattern=SEMVER_REGEX)
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = None
    collection: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("stac_version") is None:
                data["stac_version"] = STAC_VERSION
            if data.get("geometry") and data.get("bbox") is None:
                raise ValueError("bbox is required if geometry is not null")
            if data.get("assets") is None:
                data["assets"] = {}
            if data.get("links") is None:
                data["links"] = []
        return data

    # https://github.com/developmentseed/geojson-pydantic/issues/147
    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        for field in self.__geojson_exclude_if_none__:
            if field in data and data[field] is None:
                del data[field]
        return data
