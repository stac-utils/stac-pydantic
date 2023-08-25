from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class ContextExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/context#context-extension-specification
    """

    returned: int
    limit: Optional[int] = None
    matched: Optional[int] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @model_validator(mode="before")
    def validate_limit(cls, values: Dict[str, Any]) -> None:
        if values["limit"] and values["returned"] > values["limit"]:
            raise ValueError(
                "Number of returned items must be less than or equal to the limit"
            )
