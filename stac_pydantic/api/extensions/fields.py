from typing import List, Optional

from pydantic import BaseModel


class FieldsExtension(BaseModel):
    includes: Optional[List[str]]
    excludes: Optional[List[str]]