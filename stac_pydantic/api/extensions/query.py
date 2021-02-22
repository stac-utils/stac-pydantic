from enum import auto

from stac_pydantic.utils import AutoValueEnum


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
    constains = auto()
