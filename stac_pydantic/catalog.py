from typing import List, Optional

from pydantic import AnyUrl, BaseModel, Field, constr, root_validator

from stac_pydantic.links import Links
from stac_pydantic.version import STAC_VERSION


class Catalog(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md
    """

    id: constr(min_length=1)
    description: constr(min_length=1)
    stac_version: constr(min_length=1) = Field(STAC_VERSION, const=True)
    links: Links
    stac_extensions: Optional[List[AnyUrl]]
    title: Optional[str]
    type: constr(min_length=1) = Field("Catalog", const=True)

    class Config:
        use_enum_values = True
        extra = "allow"

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
