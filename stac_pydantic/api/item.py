from pydantic import model_validator

from stac_pydantic.item import Item as BaseItem
from stac_pydantic.links import Relations


class Item(BaseItem):
    @model_validator(mode="after")
    def required_links(self) -> "Item":
        links_rel = []
        for link in self.links.root:
            links_rel.append(link.rel)

        required_rels = [Relations.root, Relations.self, Relations.collection]

        for rel in required_rels:
            assert (
                rel in links_rel
            ), f"STAC API FEATURE conform Item pages must include a `{rel}` link."

        return self
