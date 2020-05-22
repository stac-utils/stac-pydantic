from typing import List

from pydantic import BaseModel, AnyHttpUrl


class ConformanceClasses(BaseModel):
    conformsTo: List[AnyHttpUrl]