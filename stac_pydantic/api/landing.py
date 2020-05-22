from typing import List, Optional, Union

from pydantic import BaseModel, Field

from ..shared import ExtensionTypes, Link
from ..version import STAC_VERSION



class LandingPage(BaseModel):
    title: str
    description: str
    stac_version: Field(STAC_VERSION, const=True)
    stac_extensions: Optional[List[Union[str, ExtensionTypes]]]
    links: List[Link]