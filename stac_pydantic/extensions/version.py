from typing import Optional

from pydantic import BaseModel


class VersionExtension(BaseModel):
    """
    https://github.com/stac-extensions/version
    """

    version: str
    deprecated: Optional[bool]
