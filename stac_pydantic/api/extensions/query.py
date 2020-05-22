from enum import auto

from ...utils import AutoValueEnum


class Operator(str, AutoValueEnum):
    eq = auto()
    ne = auto()
    lt = auto()
    le = auto()
    gt = auto()
    ge = auto()
    startsWith = auto()
    endsWith = auto()
    constains = auto()