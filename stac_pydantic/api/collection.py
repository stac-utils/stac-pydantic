from pydantic import model_validator

from stac_pydantic.collection import Collection as BaseCollection
from stac_pydantic.links import Relations


class Collection(BaseCollection):
    """
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/ogcapi-features#collection-collectionscollectionid
    """

    @model_validator(mode="after")
    def required_links(self) -> "Collection":
        links_rel = []
        for link in self.links.root:
            links_rel.append(link.rel)

        required_rels = [Relations.root, Relations.self]

        for rel in required_rels:
            assert (
                rel in links_rel
            ), f"STAC API COLLECTIONS conform Collection pages must include a `{rel}` link."

        return self
