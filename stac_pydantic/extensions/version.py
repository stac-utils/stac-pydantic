from typing import Optional

from pydantic import BaseModel


class VersionExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/version#versioning-indicators-extension-specification
    """

    version: str
    deprecated: Optional[bool]
