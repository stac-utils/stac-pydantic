from typing import Optional

from pydantic import constr, BaseModel


class VersionExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/version#item-properties-and-collection-fields
    """

    version: constr(min_length=1)
    deprecated: Optional[bool]
