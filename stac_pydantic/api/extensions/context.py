from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator

CONTEXT_VERSION = "v1.0.0-rc.2"


class ContextExtension(BaseModel):
    """
    https://github.com/stac-api-extensions/context/tree/v1.0.0-rc.2#context-object
    """

    returned: int
    limit: Optional[int] = None
    matched: Optional[int] = None

    @model_validator(mode="before")
    def validate_limit(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        from warnings import warn

        warn(
            "STAC API - Context Extension is deprecated. "
            "Please see https://github.com/stac-api-extensions/context for details.",
            DeprecationWarning,
        )

        if values["limit"] and values["returned"] > values["limit"]:
            raise ValueError(
                "Number of returned items must be less than or equal to the limit"
            )
        if values["matched"] and values["returned"] > values["matched"]:
            raise ValueError(
                "Number of returned items must be less than or equal to the matched items"
            )
        return values
