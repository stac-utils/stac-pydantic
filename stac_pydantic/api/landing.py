from typing import Literal, List, Optional

from pydantic import AnyUrl, BaseModel, Field

from stac_pydantic.links import Links
from stac_pydantic.version import STAC_VERSION


class LandingPage(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#ogc-api---features-endpoints
    """

    id: str = Field(..., alias="id", min_length=1)
    description: str = Field(..., alias="description", min_length=1)
    title: Optional[str] = None
    stac_version: Literal[STAC_VERSION] = STAC_VERSION
    stac_extensions: Optional[List[AnyUrl]] = []
    conformsTo: List[AnyUrl]
    links: Links
    type: Literal["Catalog"] = "Catalog"
