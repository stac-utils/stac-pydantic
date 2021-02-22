from typing import List

from pydantic import BaseModel

from stac_pydantic.shared import Asset


class CollectionAssetExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/collection-assets
    """

    assets: List[Asset]
