from enum import auto
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from ..shared import NumType
from ..utils import AutoValueEnum


class LabelTypes(str, AutoValueEnum):
    vector = auto()
    raster = auto()


class ClassObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/label#class-object
    """

    name: Optional[Union[str]]
    classes: Optional[List[Union[str, int]]]


class CountObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/label#count-object
    """

    name: Optional[str]
    count: Optional[int]


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/label#stats-object
    """

    name: Optional[str]
    value: Optional[NumType]


class OverviewObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/label#label-overview-object
    """

    property_key: Optional[str]
    counts: Optional[List[CountObject]]
    statistics: Optional[List[StatsObject]]


class LabelExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/label#label-extension-specification
    """

    properties: List[Union[str, None]] = Field(..., alias="label:properties")
    classes: List[ClassObject] = Field(..., alias="label:classes")
    description: str = Field(..., alias="label:description")
    type: LabelTypes = Field(..., alias="label:type")
    tasks: Optional[List[str]] = Field(None, alias="label:tasks")
    methods: Optional[List[str]] = Field(None, alias="label:methods")
    overviews: Optional[List[OverviewObject]] = Field(None, alias="label:overviews")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
