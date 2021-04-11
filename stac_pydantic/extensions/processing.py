from typing import Optional

from pydantic import BaseModel, Field


class ProcessingExtension(BaseModel):
    """
    https://github.com/stac-extensions/processing
    """

    lineage: Optional[str] = Field(None, alias="processing:lineage")
    level: Optional[str] = Field(None, alias="processing:level")
    facility: Optional[str] = Field(None, alias="processing:facility")
    software: Optional[str] = Field(None, alias="processing:software")
