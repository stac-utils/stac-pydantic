from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class TimestampsExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/timestamps
    """

    published: Optional[Union[str, datetime]] = Field(None, alias="published")
    expires: Optional[Union[str, datetime]] = Field(None, alias="expires")
    unpublished: Optional[Union[str, datetime]] = Field(None, alias="unpublished")
