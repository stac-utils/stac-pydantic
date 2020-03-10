from typing import Optional

from pydantic import BaseModel


class ContextObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/master/api-spec/extensions/context#context-extension-specification
    """

    returned: int
    limit: Optional[int]
    matched: Optional[int]
