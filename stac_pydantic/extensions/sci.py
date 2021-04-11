from typing import List, Optional

from pydantic import BaseModel, Field


class PublicationObject(BaseModel):
    """
    https://github.com/stac-extensions/scientific#publication-object
    """

    doi: Optional[str]
    citation: Optional[str]


class ScientificCitationExtension(PublicationObject):
    """
    https://github.com/stac-extensions/scientific
    """

    doi: Optional[str] = Field(None, alias="sci:doi")
    publications: Optional[List[PublicationObject]] = Field(
        None, alias="sci:publications"
    )
    citation: Optional[str] = Field(None, alias="sci:citation")

    class Config:
        allow_population_by_field_name = True
