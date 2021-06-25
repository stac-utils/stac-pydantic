from enum import Enum
from typing import Dict, Optional, Type

from pydantic import BaseModel


class AutoValueEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
