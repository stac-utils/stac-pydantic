from typing import Any, Dict, List

from pydantic import BaseModel

from ..collection import Collection
from ..links import Link


class Collections(BaseModel):
    """
    http://docs.opengeospatial.org/is/17-069r3/17-069r3.html#_feature_collections_rootcollections
    """

    links: List[Link]
    collections: List[Collection]

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs: Any) -> str:
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
