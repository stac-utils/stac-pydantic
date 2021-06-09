from enum import auto

from pydantic import BaseModel

from stac_pydantic.utils import AutoValueEnum


class SortDirections(str, AutoValueEnum):
    asc = auto()
    desc = auto()


class SortExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/sort#sort-api-extension
    """

    field: const(min_length=1)
    direction: SortDirections
