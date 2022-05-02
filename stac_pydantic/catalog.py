from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Field

from stac_pydantic.links import Links
from stac_pydantic.version import STAC_VERSION


class Catalog(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: str = Field(..., alias="", min_length=1)
    description: str = Field(..., alias="description", min_length=1)
    stac_version: str = Field(STAC_VERSION, const=True, min_length=1)
    links: Links
    stac_extensions: Optional[List[AnyUrl]]
    title: Optional[str]
    type: str = Field("Catalog", const=True, min_length=1)

    class Config:
        use_enum_values = True
        extra = "allow"

    def to_dict(self: "Catalog", **kwargs: Any) -> Dict[str, Any]:
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self: "Catalog", **kwargs: Any) -> str:
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
