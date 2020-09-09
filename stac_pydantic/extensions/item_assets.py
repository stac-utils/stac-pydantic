from typing import List, Optional

from pydantic import BaseModel

from ..shared import Asset


class CollectionAsset(Asset):
    href: Optional[str]


class ItemAssetExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/item-assets
    """

    item_assets: List[CollectionAsset]
