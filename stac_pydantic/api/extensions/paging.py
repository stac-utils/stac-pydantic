from enum import auto
from typing import Any, Dict, Optional

from ...shared import Link
from ...utils import AutoValueEnum


class PaginationMethods(str, AutoValueEnum):
    GET = auto()
    POST = auto()

class PaginationRelations(str, AutoValueEnum):
    next = auto()
    previous = auto()

class PaginationLink(Link):
    rel: PaginationRelations
    method: PaginationMethods
    body: Optional[Dict[Any, Any]]
    merge: bool = False