from typing import List, Optional

from pydantic import BaseModel


class PublicationObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/scientific#publication-object
    """

    doi: Optional[str]
    citation: Optional[str]


class ScientificExtension(PublicationObject):
    """
    https://github.com/radiantearth/stac-spec/tree/v0.9.0/extensions/scientific#item-and-collection-fields
    """

    doi: Optional[str]
    publications: Optional[List[PublicationObject]]
    citation: Optional[str]

    class Config:
        allow_population_by_field_name = True
        alias_generator = lambda field_name: f"sci:{field_name}"
