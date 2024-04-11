from typing import List, Literal, Optional

from pydantic import AnyUrl, ConfigDict, Field

from stac_pydantic.links import Links
from stac_pydantic.shared import SEMVER_REGEX, StacBaseModel
from stac_pydantic.version import STAC_VERSION


class _Catalog(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    description: str = Field(..., alias="description", min_length=1)
    stac_version: str = Field(STAC_VERSION, pattern=SEMVER_REGEX)
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = []
    title: Optional[str] = None
    type: str
    model_config = ConfigDict(use_enum_values=True, extra="allow")


class Catalog(_Catalog):
    type: Literal["Catalog"]
