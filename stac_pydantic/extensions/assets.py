from typing import Dict, List, Optional

from pydantic import BaseModel

from ..shared import AssetRoles


class CollectionAsset(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/asset#asset-object
    """

    type: Optional[str]
    title: Optional[str]
    description: Optional[str]
    roles: Optional[List[AssetRoles]]


class AssetExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/asset#asset-definition-specification
    """

    assets: Dict[str, CollectionAsset]
