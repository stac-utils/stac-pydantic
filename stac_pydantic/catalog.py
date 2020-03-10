from typing import List, Optional

from pydantic import BaseModel, root_validator

from .shared import ExtensionTypes, Link
from .extensions import Extensions


class Catalog(BaseModel):
    id: str
    description: str
    stac_version: str
    stac_extensions: Optional[List[ExtensionTypes]]
    title: Optional[str]
    links: List[Link]

    class Config:
        use_enum_values = True
        extra = "allow"

    @root_validator(pre=True)
    def validate_extensions(cls, values):
        if "stac_extensions" in values:
            if values["stac_extensions"]:
                for ext in values["stac_extensions"]:
                    if "http" not in ext:
                        ext_model = getattr(Extensions, ext)
                        ext_model(**values)
        return values

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


stac_catalog = {
    "id": "test-catalog",
    "description": "test",
    "stac_version": "0.0.9",
    "links": {

    }
}