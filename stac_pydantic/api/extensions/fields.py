from typing import Optional, Set

from pydantic import BaseModel


class FieldsExtension(BaseModel):
    includes: Optional[Set[str]]
    excludes: Optional[Set[str]]