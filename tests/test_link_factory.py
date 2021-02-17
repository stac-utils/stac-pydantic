from typing import ClassVar, Tuple
from urllib.parse import urljoin

from stac_pydantic.api.utils.link_factory import BaseLinks, CollectionLinks, ItemLinks
from stac_pydantic.links import Link


def test_collection_links():
    links = CollectionLinks(
        collection_id="collection", base_url="http://stac.com"
    ).create_links()
    for link in links:
        assert isinstance(link, Link)
        assert link.rel in CollectionLinks._link_members


def test_item_links():
    links = ItemLinks(
        collection_id="collection", item_id="item", base_url="http://stac.com"
    ).create_links()
    for link in links:
        assert isinstance(link, Link)
        assert link.rel in ItemLinks._link_members


def test_custom_links():
    class CustomLinks(BaseLinks):
        _link_members: ClassVar[Tuple[str]] = ("another_link",)

        def another_link(self) -> Link:
            return Link(
                rel="another-link",
                type="application/json",
                href=urljoin(self.base_url, "/another-link"),
            )

    links = CustomLinks(base_url="http://stac.com").create_links()
    assert len(links) == 1
    assert links[0].rel == "another-link"
    assert links[0].type == "application/json"
    assert links[0].href == "http://stac.com/another-link"
