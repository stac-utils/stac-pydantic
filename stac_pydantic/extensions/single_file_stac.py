from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..collection import Collection
from ..item import ItemCollection


class SearchObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/single-file-stac#search-object
    """

    endpoint: Optional[str]
    parameters: Optional[Dict[Any, Any]]


class SingleFileStac(ItemCollection):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/single-file-stac#single-file-stac-specification
    """

    collections: List[Collection]
    search: SearchObject

    def to_dict(self):
        return self.dict(by_alias=True, exclude_unset=True)
