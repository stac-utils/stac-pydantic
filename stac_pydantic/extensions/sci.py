from typing import List, Optional

from pydantic import BaseModel


class PublicationObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/scientific#publication-object
    """

    doi: Optional[str]
    citation: Optional[str]


class ScientificExtension(PublicationObject):
    """
    https://github.com/radiantearth/stac-spec/blob/v0.0.9/extensions/scientific#scientific-extension-specification
    """

    doi: Optional[str]
    publications: Optional[List[PublicationObject]]
    citation: Optional[str]

    class Config:
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"sci:{field_name}"
