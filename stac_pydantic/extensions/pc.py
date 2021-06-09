from enum import auto
from typing import List, Optional

from pydantic import constr, BaseModel, Field

from stac_pydantic.shared import NumType
from stac_pydantic.utils import AutoValueEnum


class ChannelTypes(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/pointcloud#schema-object
    """

    floating = auto()
    unsigned = auto()
    signed = auto()


class SchemaObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/pointcloud#schema-object
    """

    name: constr(min_length=1)
    size: int
    type: ChannelTypes

    class Config:
        use_enum_values = True


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/pointcloud#stats-object
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
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/pointcloud#point-cloud-extension-specification
    """

    count: int = Field(..., alias="pc:count")
    type: constr(min_length=1) = Field(..., alias="pc:type")
    encoding: constr(min_length=1) = Field(..., alias="pc:encoding")
    schemas: List[SchemaObject] = Field(..., alias="pc:schemas")
    density: Optional[int] = Field(None, alias="pc:density")
    statistics: Optional[List[StatsObject]] = Field(None, alias="pc:statistics")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
