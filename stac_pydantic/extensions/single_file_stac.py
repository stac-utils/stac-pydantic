from typing import List

from stac_pydantic import Collection, ItemCollection


class SingleFileStac(ItemCollection):
    """
    https://github.com/stac-extensions/single-file-stac
    """

    collections: List[Collection]

    def to_dict(self):
        return self.dict(by_alias=True, exclude_unset=True)
