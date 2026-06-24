from typing import ClassVar
from urllib.parse import urljoin, urlsplit

import pytest

from stac_pydantic.api.utils.link_factory import BaseLinks, CollectionLinks, ItemLinks
from stac_pydantic.links import Link
from stac_pydantic.shared import MimeTypes


@pytest.mark.parametrize(
    "base_url",
    [
        "http://stac.com",
        "http://stac.com/v1/stac",
    ],
)
def test_base_links(base_url) -> None:
    links = BaseLinks(
        base_url=base_url,
    ).create_links()
    for link in links.link_iterator():
        assert isinstance(link, Link)
        assert link.rel in BaseLinks._link_members
        assert link.href.startswith(base_url)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://stac.com",
        "http://stac.com/v1/stac",
    ],
)
def test_collection_links(base_url) -> None:
    links = CollectionLinks(
        collection_id="collection",
        base_url=base_url,
    ).create_links()
    for link in links.link_iterator():
        assert isinstance(link, Link)
        assert link.rel in CollectionLinks._link_members
        assert link.href.startswith(base_url)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://stac.com",
        "http://stac.com/v1/stac",
    ],
)
def test_item_links(base_url) -> None:
    links = ItemLinks(
        collection_id="collection",
        item_id="item",
        base_url=base_url,
    ).create_links()
    for link in links.link_iterator():
        assert isinstance(link, Link)
        assert link.rel in ItemLinks._link_members
        assert link.href.startswith(base_url)


@pytest.mark.parametrize(
    "base_url,expected_href",
    [
        ("http://stac.com", "http://stac.com/another-link"),
        ("http://stac.com/v1/stac", "http://stac.com/v1/stac/another-link"),
    ],
)
def test_custom_links(base_url, expected_href) -> None:
    class CustomLinks(BaseLinks):
        _link_members: ClassVar[tuple[str]] = ("another_link",)

        def another_link(self) -> Link:
            path = urlsplit(self.base_url).path.rstrip("/")
            return Link(
                rel="another-link",
                type=MimeTypes.json,
                href=urljoin(self.base_url, f"{path}/another-link"),
            )

    links = CustomLinks(base_url=base_url).create_links()
    assert len(links) == 1
    assert links[0].rel == "another-link"
    assert links[0].type == "application/json"
    assert links[0].href == expected_href
