from typing import List, Optional

from pydantic import model_validator

from stac_pydantic.api.collection import Collection
from stac_pydantic.api.links import Links
from stac_pydantic.links import Relations
from stac_pydantic.shared import StacBaseModel


class Collections(StacBaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/ogcapi-features#endpoints
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/ogcapi-features#collections-collections
    """

    links: Links
    collections: List[Collection]
    numberMatched: Optional[int] = None
    numberReturned: Optional[int] = None

    @model_validator(mode="after")
    def required_links(self) -> "Collections":
        links_rel = []
        for link in self.links.root:
            links_rel.append(link.rel)

        required_rels = [Relations.root, Relations.self]

        for rel in required_rels:
            assert (
                rel in links_rel
            ), f"STAC API COLLECTIONS conform Collections pages must include a `{rel}` link."

        return self
