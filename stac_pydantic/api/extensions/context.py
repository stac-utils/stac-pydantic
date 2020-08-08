from typing import Optional

from pydantic import BaseModel, validator


class ContextExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/context#context-extension-specification
    """

    returned: int
    limit: Optional[int]
    matched: Optional[int]

    @validator("limit")
    def validate_limit(cls, v, values):
        if values["returned"] > v:
            raise ValueError(
                "Number of returned items must be less than or equal to the limit"
            )
