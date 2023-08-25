import json
from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Union, Literal

from geojson_pydantic.features import Feature, FeatureCollection  # type: ignore
from pydantic import model_validator, ConfigDict, AnyUrl, Field, field_validator, TypeAdapter, field_serializer
parse_datetime = lambda x: TypeAdapter(dt).validate_json(json.dumps(x))

from stac_pydantic.api.extensions.context import ContextExtension
from stac_pydantic.links import Links
from stac_pydantic.shared import DATETIME_RFC339, Asset, StacCommonMetadata
from stac_pydantic.version import STAC_VERSION


class ItemProperties(StacCommonMetadata):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md#properties-object
    """

    datetime: Union[dt, str] = Field(..., alias="datetime")

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @field_validator("datetime", mode="before")
    def validate_datetime(cls, v: Union[dt, str], values: Dict[str, Any]) -> dt:
        if v == "null":
            if not values["start_datetime"] and not values["end_datetime"]:
                raise ValueError(
                    "start_datetime and end_datetime must be specified when datetime is null"
                )

        if isinstance(v, str):
            v = parse_datetime(v)

        return v

    @field_serializer("datetime")
    def serialize_datetime(self, v: dt, _info):
        return v.strftime(DATETIME_RFC339)

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(extra="allow")


class Item(Feature):  # type: ignore
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    stac_version: Literal[STAC_VERSION] = STAC_VERSION
    properties: ItemProperties
    assets: Dict[str, Asset]
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = []
    collection: Optional[str] = None

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_unset=True, **kwargs)  # type: ignore

    def to_json(self, **kwargs: Any) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=True, **kwargs)  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def validate_bbox(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values, dict):
            if values.get("geometry") and values.get("bbox") is None:
                raise ValueError("bbox is required if geometry is not null")
        return values


class ItemCollection(FeatureCollection):  # type: ignore
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/itemcollection-spec.md
    """

    stac_version: Literal[STAC_VERSION] = STAC_VERSION
    features: List[Item]
    stac_extensions: Optional[List[AnyUrl]] = []
    links: Links
    context: Optional[ContextExtension] = None

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_unset=True, **kwargs)  # type: ignore

    def to_json(self, **kwargs: Any) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=True, **kwargs)  # type: ignore
