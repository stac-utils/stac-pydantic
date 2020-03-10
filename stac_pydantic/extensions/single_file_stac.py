from typing import Any, Dict, List

from pydantic import BaseModel

from ..collection import Collection
from ..item import ItemCollection


class SearchObject(BaseModel):
    endpoint: str
    parameters: Dict[Any, Any]


class SingleFileStac(ItemCollection):
    collections: List[Collection]
    search: SearchObject

    def to_dict(self):
        return self.dict(by_alias=True, exclude_unset=True)
