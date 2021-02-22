from typing import List, Optional, Union

from pydantic import BaseModel, Field

from stac_pydantic.links import Links
from stac_pydantic.shared import ExtensionTypes
from stac_pydantic.version import STAC_VERSION


class LandingPage(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#ogc-api---features-endpoints
    """

    id: str
    description: str
    title: Optional[str]
    stac_version: str = Field(STAC_VERSION, const=True)
    stac_extensions: Optional[List[Union[str, ExtensionTypes]]]
    links: Links
