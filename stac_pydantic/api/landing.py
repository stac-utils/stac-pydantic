from typing import List

from pydantic import AnyUrl, HttpUrl, model_validator

from stac_pydantic.api.links import Links
from stac_pydantic.api.version import STAC_API_VERSION
from stac_pydantic.catalog import Catalog
from stac_pydantic.links import Relations


class LandingPage(Catalog):
    """
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/core
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/ogcapi-features#landing-page-
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/item-search#link-relations
    """

    conformsTo: List[AnyUrl] = [
        HttpUrl("https://api.stacspec.org/v1.0.0/core"),
        HttpUrl("http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core"),
    ]
    links: Links

    @model_validator(mode="after")
    def required_links(self) -> "LandingPage":
        links_rel = []
        for link in self.links.root:
            links_rel.append(link.rel)

        required_core_rels = [Relations.root, Relations.self, Relations.service_desc]

        for rel in required_core_rels:
            assert (
                rel in links_rel
            ), f"STAC API conform Landing pages must include a `{rel}` link."

        if (
            AnyUrl(f"https://api.stacspec.org/v{STAC_API_VERSION}/collections")
            in self.conformsTo
        ):
            required_collections_rels = [Relations.data]
            for rel in required_collections_rels:
                assert (
                    rel in links_rel
                ), f"STAC API COLLECTION conform Landing pages must include a `{rel}` link."

        if (
            AnyUrl(f"https://api.stacspec.org/v{STAC_API_VERSION}/item-search")
            in self.conformsTo
        ):
            required_feature_rels = [Relations.search]
            for rel in required_feature_rels:
                assert (
                    rel in links_rel
                ), f"STAC API ITEM SEARCH conform Landing pages must include a `{rel}` link."

        return self
