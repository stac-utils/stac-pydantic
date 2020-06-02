from enum import auto

from pydantic import BaseModel

from ...utils import AutoValueEnum


class SortDirections(str, AutoValueEnum):
    asc = auto()
    desc = auto()


class SortExtension(BaseModel):
    field: str
    direction: SortDirections