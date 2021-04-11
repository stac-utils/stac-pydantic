from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator

from stac_pydantic.extensions import Extensions
from stac_pydantic.links import Links
from stac_pydantic.shared import NumType
from stac_pydantic.version import STAC_VERSION


class Stats(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/collection-spec/collection-spec.md#stats-object
    """

    min: Union[NumType, str]
    max: Union[NumType, str]


class Catalog(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0-beta.1/catalog-spec/catalog-spec.md
    """

    type: str = Field("Catalog", const=True)
    id: str
    description: str
    stac_version: str = Field(STAC_VERSION, const=True)
    links: Links
    stac_extensions: Optional[List[str]]
    title: Optional[str]
    summaries: Optional[Dict[str, Union[Stats, List[Any]]]]

    class Config:
        use_enum_values = True
        extra = "allow"

    @root_validator(pre=True)
    def validate_extensions(cls, values):
        if "stac_extensions" in values:
            for ext in values["stac_extensions"]:
                if ext in ("collection-assets", "item-assets", "version"):
                    ext_model = Extensions.get(ext)
                    ext_model(**values)
        return values

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
