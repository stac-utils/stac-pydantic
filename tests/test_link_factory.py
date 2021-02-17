from stac_pydantic.api.utils.link_factory import CollectionLinks, ItemLinks
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
