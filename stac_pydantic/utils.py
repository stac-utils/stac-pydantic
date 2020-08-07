from enum import Enum
from typing import Dict, Type

from pydantic import BaseModel


class AutoValueEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def decompose_model(model: Type[BaseModel]) -> Dict:
    """Decompose a pydantic model into a dictionary of model fields"""
    return {k: (v.outer_type_, v.field_info) for (k, v) in model.__fields__.items()}
