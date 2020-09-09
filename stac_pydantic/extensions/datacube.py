from enum import auto
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from ..shared import NumType
from ..utils import AutoValueEnum


class HorizontalAxis(str, AutoValueEnum):
    x = auto()
    y = auto()


class DimensionObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/datacube#additional-dimension-object
    """

    type: str
    description: Optional[str]
    extent: Optional[Tuple[NumType, NumType]]
    values: Optional[List[Union[NumType, str]]]
    step: Optional[Union[NumType, str]]
    unit: Optional[str]
    reference_system: Optional[int]
    axis: Optional[str]


class HorizontalSpatialDimension(DimensionObject):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/datacube#horizontal-spatial-dimension-object
    """

    type: str = Field("spatial", const=True)
    axis: HorizontalAxis
    extent: List[NumType]

    class Config:
        use_enum_values = True


class VerticalSpatialDimension(HorizontalSpatialDimension):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/datacube#vertical-spatial-dimension-object
    """

    axis: str = Field("z", const=True)


class TemporalDimension(DimensionObject):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/datacube#temporal-dimension-object
    """

    type: str = Field("temporal", const=True)
    extent: Tuple[NumType, NumType]


class DatacubeExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/datacube#data-cube-extension-specification
    """

    dimensions: Dict[
        str,
        Union[
            HorizontalSpatialDimension,
            VerticalSpatialDimension,
            TemporalDimension,
            DimensionObject,
        ],
    ] = Field(..., alias="cube:dimensions")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
