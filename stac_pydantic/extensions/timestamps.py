from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class TimestampsExtension(BaseModel):
    """
    https://github.com/stac-extensions/timestamps
    """

    published: Optional[Union[str, datetime]] = Field(None, alias="published")
    expires: Optional[Union[str, datetime]] = Field(None, alias="expires")
    unpublished: Optional[Union[str, datetime]] = Field(None, alias="unpublished")
