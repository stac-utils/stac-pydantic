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
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#class-object
    """

    name: Union[str, None]
    classes: List[Union[str, NumType]]


class CountObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#count-object
    """

    name: str
    count: int


class StatsObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#stats-object
    """

    name: str
    value: NumType


class OverviewObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-overview-object
    """

    property_key: str
    counts: Optional[List[CountObject]]
    statistics: Optional[List[StatsObject]]


class LabelExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/label#label-extension-specification
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
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"label:{field_name}"
