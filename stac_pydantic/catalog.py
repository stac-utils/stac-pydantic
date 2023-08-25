from typing import Any, Dict, List, Optional, Literal

from pydantic import ConfigDict, AnyUrl, BaseModel, Field

from stac_pydantic.links import Links
from stac_pydantic.version import STAC_VERSION


class Catalog(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: str = Field(..., alias="id", min_length=1)
    description: str = Field(..., alias="description", min_length=1)
    stac_version: Literal[STAC_VERSION] = STAC_VERSION
    links: Links
    stac_extensions: Optional[List[AnyUrl]] = []
    title: Optional[str] = None
    type: Literal["Catalog"] = "Catalog"

    model_config = ConfigDict(use_enum_values=True, extra="allow")

    def to_dict(self: "Catalog", **kwargs: Any) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self: "Catalog", **kwargs: Any) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=True, **kwargs)
