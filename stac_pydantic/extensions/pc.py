from enum import auto
from typing import List, Optional

from pydantic import BaseModel

from ..shared import NumType
from ..utils import AutoValueEnum


class ChannelTypes(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/pointcloud#schema-object
    """

    floating = auto()
    unsigned = auto()
    signed = auto()


class SchemaObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/pointcloud#schema-object
    """

    name: str
    size: int
    type: ChannelTypes


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/pointcloud#stats-object
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
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/pointcloud#point-cloud-extension-specification
    """

    count: int
    type: str
    encoding: str
    schemas: List[SchemaObject]
    density: Optional[int]
    statistics: Optional[List[StatsObject]]

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        alias_generator = lambda field_name: f"pc:{field_name}"
