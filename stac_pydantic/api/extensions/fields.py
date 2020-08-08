from typing import Optional, Set

from pydantic import BaseModel


class FieldsExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/fields#fields-api-extension
    """

    includes: Optional[Set[str]]
    excludes: Optional[Set[str]]
