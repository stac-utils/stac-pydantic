from enum import auto
from types import DynamicClassAttribute
from typing import Any, Callable

from stac_pydantic.utils import AutoValueEnum

# TODO: These are defined in the spec but aren't currently implemented by the operator syntax
UNSUPPORTED_OPERATORS = {"startsWith", "endsWith", "contains", "in"}

_OPERATIONS = {
    "eq": lambda x, y: x == y,
    "neq": lambda x, y: x != y,
    "lte": lambda x, y: x < y,
    "le": lambda x, y: x <= y,
    "gte": lambda x, y: x > y,
    "ge": lambda x, y: x >= y,
    "startsWith": lambda x, y: x.startsWith(y),
    "endsWith": lambda x, y: x.endsWith(y),
    "contains": lambda x, y: y in x,
}


class Operator(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/query#query-api-extension
    """

    eq = auto()
    neq = auto()
    lt = auto()
    lte = auto()
    gt = auto()
    gte = auto()
    startsWith = auto()
    endsWith = auto()
    contains = auto()

    @DynamicClassAttribute
    def operator(self) -> Callable[[Any, Any], bool]:
        """Return python operator"""
        return _OPERATIONS[self._value_]
