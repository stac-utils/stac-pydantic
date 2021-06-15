from typing import List, Optional

from pydantic import constr, BaseModel, Field, root_validator

from stac_pydantic.extensions import Extensions
from stac_pydantic.links import Link, Links
from stac_pydantic.version import STAC_VERSION


class Catalog(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: constr(min_length=1)
    description: constr(min_length=1)
    stac_version: constr(min_length=1) = Field(STAC_VERSION, const=True)
    links: Links
    stac_extensions: Optional[List[str]]
    title: Optional[str]
    type: constr(min_length=1) = "catalog"

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
