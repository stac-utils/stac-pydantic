from typing import Optional

from pydantic import BaseModel


class VersionExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/version#item-properties-and-collection-fields
    """

    version: str
    deprecated: Optional[bool]
