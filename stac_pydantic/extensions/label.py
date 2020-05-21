from enum import auto
from typing import List, Optional, Union

from pydantic import BaseModel

from ..shared import NumType
from ..utils import AutoValueEnum


class LabelTypes(str, AutoValueEnum):
    vector = auto()
    raster = auto()


class ClassObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/label#class-object
    """

    name: Optional[Union[str]]
    classes: Optional[List[Union[str, NumType]]]


class CountObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/label#count-object
    """

    name: Optional[str]
    count: Optional[int]


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/label#stats-object
    """

    name: Optional[str]
    value: Optional[NumType]


class OverviewObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/label#label-overview-object
    """

    property_key: Optional[str]
    counts: Optional[List[CountObject]]
    statistics: Optional[List[StatsObject]]


class LabelExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/label#label-extension-specification
    """

    properties: List[Union[str, None]]
    classes: List[ClassObject]
    description: str
    type: LabelTypes
    tasks: Optional[List[str]]
    methods: Optional[List[str]]
    overviews: Optional[List[OverviewObject]]

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        alias_generator = lambda field_name: f"label:{field_name}"
