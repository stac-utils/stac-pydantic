import operator
from enum import auto
from types import DynamicClassAttribute
from typing import Any, Callable

from stac_pydantic.utils import AutoValueEnum

# TODO: These are defined in the spec but aren't currently implemented by the operator syntax
UNSUPPORTED_OPERATORS = {"startsWith", "endsWith", "contains", "in"}


class Operator(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/query#query-api-extension
    """

    eq = auto()
    ne = auto()
    lt = auto()
    le = auto()
    gt = auto()
    ge = auto()
    startsWith = auto()
    endsWith = auto()
    contains = auto()

    @DynamicClassAttribute
    def operator(self) -> Callable[[Any, Any], bool]:
        """Return python operator"""
        if self._value_ in UNSUPPORTED_OPERATORS:
            raise NotImplementedError
        return getattr(operator, self._value_)
