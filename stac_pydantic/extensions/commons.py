from typing import Any, Dict

from pydantic import BaseModel


class CommonsExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/commons
    """

    properties: Dict[Any, Any]
