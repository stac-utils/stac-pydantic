from typing import List, Optional

from pydantic import BaseModel, Field


class PublicationObject(BaseModel):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/scientific#publication-object
    """

    doi: Optional[str]
    citation: Optional[str]


class ScientificExtension(PublicationObject):
    """
    https://github.com/radiantearth/stac-spec/tree/v1.0.0-beta.1/extensions/scientific#item-and-collection-fields
    """

    doi: Optional[str] = Field(None, alias="sci:doi")
    publications: Optional[List[PublicationObject]] = Field(
        None, alias="sci:publications"
    )
    citation: Optional[str] = Field(None, alias="sci:citation")

    class Config:
        allow_population_by_field_name = True
