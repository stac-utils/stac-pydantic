from typing import Dict, Optional

from pydantic import BaseModel

from stac_pydantic.shared import Asset


class CollectionAsset(Asset):
    """Asset described in Collection

    https://github.com/radiantearth/stac-spec/blob/master/extensions/item-assets/README.md#asset-object
    """

    # href is required in base Asset but optional in collection Asset
    href: Optional[str]


class ItemAssetExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/item-assets
    """

    item_assets: Dict[str, CollectionAsset]
