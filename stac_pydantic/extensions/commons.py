from typing import Any, Dict

from pydantic import BaseModel


class CommonsExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/master/extensions/asset#asset-object
    """

    properties: Dict[Any, Any]
