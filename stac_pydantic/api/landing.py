from typing import List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, constr

from stac_pydantic.links import Links
from stac_pydantic.version import STAC_VERSION


class LandingPage(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#ogc-api---features-endpoints
    """

    id: constr(min_length=1)
    description: constr(min_length=1)
    title: Optional[str]
    stac_version: str = Field(STAC_VERSION, const=True)
    stac_extensions: Optional[List[AnyUrl]]
    conformsTo: List[AnyUrl]
    links: Links
    type: constr(min_length=1) = Field("Catalog", const=True)
