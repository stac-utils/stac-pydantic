import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, List

from pydantic import TypeAdapter


class AutoValueEnum(Enum):
    def _generate_next_value_(  # type: ignore
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        return name


parse_datetime: Callable[[Any], datetime] = lambda x: TypeAdapter(
    datetime
).validate_json(json.dumps(x))
