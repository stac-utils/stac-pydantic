from enum import auto

from pydantic import BaseModel

from ...utils import AutoValueEnum


class SortDirections(str, AutoValueEnum):
    asc = auto()
    desc = auto()


class SortExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/sort#sort-api-extension
    """

    field: str
    direction: SortDirections
