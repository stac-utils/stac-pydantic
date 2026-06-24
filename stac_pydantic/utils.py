from enum import Enum
from typing import Any


class AutoValueEnum(Enum):
    def _generate_next_value_(  # type: ignore
        name: str, start: int, count: int, last_values: list[Any]
    ) -> Any:
        return name
