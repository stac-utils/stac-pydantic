from enum import auto
from typing import List, Optional

from pydantic import BaseModel

from ..shared import NumType
from ..utils import AutoValueEnum


class ChannelTypes(str, AutoValueEnum):
    floating = auto()
    unsigned = auto()
    signed = auto()


class SchemaObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    name: str
    size: int
    type: ChannelTypes


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    average: Optional[NumType]
    count: Optional[int]
    maximum: Optional[NumType]
    minimum: Optional[NumType]
    name: Optional[str]
    position: Optional[int]
    stddev: Optional[NumType]
    variance: Optional[NumType]


class PointCloudExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    count: int
    type: str
    encoding: str
    schemas: List[SchemaObject]
    density: Optional[int]
    statistics: List[StatsObject]

    class Config:
        use_enum_values = True
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"pc:{field_name}"
