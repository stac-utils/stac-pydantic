from typing import Any, List, Literal, Optional

from pydantic import AnyUrl, ConfigDict, Field, model_validator

from stac_pydantic.links import Links
from stac_pydantic.shared import SEMVER_REGEX, StacBaseModel
from stac_pydantic.version import STAC_VERSION


class _Catalog(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    description: str = Field(..., alias="description", min_length=1)
    stac_version: str = Field(..., pattern=SEMVER_REGEX)
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = None
    title: Optional[str] = None
    type: str
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def set_default_links(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("links") is None:
                data["links"] = []
            if data.get("stac_version") is None:
                data["stac_version"] = STAC_VERSION
        return data


class Catalog(_Catalog):
    type: Literal["Catalog"]
