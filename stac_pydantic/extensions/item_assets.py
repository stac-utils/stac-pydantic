from typing import Dict, Optional

from pydantic import BaseModel

from stac_pydantic.shared import Asset


class CollectionAsset(Asset):
    """
    https://github.com/stac-extensions/item-assets#asset-object
    """

    # href is required in base Asset but optional in collection Asset
    href: Optional[str]


class ItemAssetExtension(BaseModel):
    """
    https://github.com/stac-extensions/item-assets
    """

    item_assets: Dict[str, CollectionAsset]
