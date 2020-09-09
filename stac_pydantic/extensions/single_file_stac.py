from typing import List

from ..collection import Collection
from ..item import ItemCollection


class SingleFileStac(ItemCollection):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/single-file-stac#single-file-stac-specification
    """

    collections: List[Collection]

    def to_dict(self):
        return self.dict(by_alias=True, exclude_unset=True)
