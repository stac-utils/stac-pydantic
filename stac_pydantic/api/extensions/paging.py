from enum import auto
from typing import Any, Dict, Optional

from ...shared import Link
from ...utils import AutoValueEnum


class PaginationMethods(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#paging-extension
    """

    GET = auto()
    POST = auto()


class PaginationRelations(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#paging-extension
    """

    next = auto()
    previous = auto()


class PaginationLink(Link):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#paging-extension
    """

    rel: PaginationRelations
    method: PaginationMethods
    body: Optional[Dict[Any, Any]]
    merge: bool = False
