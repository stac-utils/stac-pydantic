from typing import Optional, Sequence
from urllib.parse import urlparse

from pydantic import model_validator

from stac_pydantic.api.item import Item
from stac_pydantic.api.links import Links
from stac_pydantic.item_collection import ItemCollection as BaseItemCollection
from stac_pydantic.links import Relations


class ItemCollection(BaseItemCollection):
    """
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/fragments/itemcollection/README.md
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#link-relations
    """

    features: Sequence[Item]
    links: Optional[Links] = None
    numberMatched: Optional[int] = None
    numberReturned: Optional[int] = None

    @model_validator(mode="after")
    def required_links(self) -> "ItemCollection":
        if self.links:
            links_rel = [link.rel for link in self.links.root]
            if Relations.self in links_rel:
                self_href = [link for link in self.links.root if link.rel == "self"][0]
                item_collection_type = urlparse(self_href.href).path.split("/")[-1]

                if item_collection_type == "items":
                    required_links = [
                        Relations.root,
                        Relations.self,
                        Relations.collection,
                    ]
                    for link in required_links:
                        assert (
                            link in links_rel
                        ), f"STAC API FEATURES conform Items pages must include a `{link}` link."

                if item_collection_type == "search":
                    required_links = [Relations.root]
                    for link in required_links:
                        assert (
                            link in links_rel
                        ), f"STAC API FEATURES conform Items pages must include a `{link}` link."

        return self
