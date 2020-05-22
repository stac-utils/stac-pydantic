from typing import Optional

from pydantic import BaseModel


class ContextExtension(BaseModel):
    returned: int
    limit: Optional[int]
    matched: Optional[int]