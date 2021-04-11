from enum import auto
from typing import Any, Optional

from pydantic import BaseModel, Field

from stac_pydantic.utils import AutoValueEnum


class DataTypes(str, AutoValueEnum):
    """
    https://github.com/stac-extensions/file#data-types
    """

    int8 = auto()
    int16 = auto()
    int32 = auto()
    int64 = auto()
    uint8 = auto()
    uint16 = auto()
    uint32 = auto()
    uint64 = auto()
    float13 = auto()
    float32 = auto()
    float64 = auto()
    cint16 = auto()
    cint32 = auto()
    cfloat32 = auto()
    cfloat64 = auto()
    other = auto()


class ValueMapping(BaseModel):
    """
    https://github.com/stac-extensions/file#mapping-object
    """

    value: Any
    summary: str


class FileInfoExtension(BaseModel):
    """
    https://github.com/stac-extensions/file
    """

    bits_per_sample: Optional[int] = Field(None, alias="file:bits_per_sample")
    byte_order: Optional[str] = Field(None, alias="file:byte_order")
    checksum: Optional[str] = Field(None, alias="file:checksum")
    data_type: Optional[DataTypes] = Field(None, alias="file:data_type")
    header_size: Optional[int] = Field(None, alias="file:header_size")
    nodata: Optional[Any] = Field(None, alias="file:nodata")
    size: Optional[int] = Field(None, alias="file:size")
    unit: Optional[str] = Field(None, alias="file:unit")
    values: Optional[ValueMapping] = Field(None, alias="file:values")
