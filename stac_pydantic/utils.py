from enum import Enum
from typing import Dict, Optional, Type

from pydantic import BaseModel


class AutoValueEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def decompose_model(model: Type[BaseModel]) -> Dict:
    """Decompose a pydantic model into a dictionary of model fields"""
    fields = {}
    for (k, v) in model.__fields__.items():
        type = v.outer_type_
        if not v.required:
            type = Optional[type]
        fields[k] = (type, v.field_info)
    return fields
