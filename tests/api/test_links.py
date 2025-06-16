import pytest
from pydantic import ValidationError

from stac_pydantic.api import ItemCollection
from stac_pydantic.api.links import Link, Links, PaginationLink, Relations, SearchLink
from stac_pydantic.api.version import STAC_API_VERSION
from stac_pydantic.links import MimeTypes
from stac_pydantic.version import STAC_VERSION

from ..conftest import request

PATH = ["tests", "api", "examples", f"v{STAC_API_VERSION}"]
ITEM_COLLECTION = "itemcollection-sample-full.json"


def test_links():
    example = request(
        "links.json", ["tests", "api", "examples", f"v{STAC_API_VERSION}"]
    )["links"]
    links = Links(example)
    for link in links.root:
        assert isinstance(link, Link)
        if link.rel in [Relations.search, Relations.next, Relations.prev]:
            assert isinstance(link, SearchLink)


def test_api_invalid_paging_link():
    # Invalid rel type
    with pytest.raises(ValidationError):
        PaginationLink(rel="self", method="GET", href="http://next")

    # Invalid method
    with pytest.raises(ValidationError):
        PaginationLink(rel="next", method="DELETE", href="http://next")


def test_api_paging_extension():
    item_collection = request(ITEM_COLLECTION, PATH)
    item_collection["stac_version"] = STAC_VERSION
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION
    item_collection["links"] += [
        {
            "title": "next page",
            "rel": Relations.next,
            "method": "GET",
            "href": "http://my.stac.com/search?next",
            "type": MimeTypes.geojson,
        },
        {
            "title": "previous page",
            "rel": Relations.prev,
            "method": "POST",
            "href": "http://my.stac.com/search?prev",
            "body": {"key": "value"},
            "type": MimeTypes.geojson,
        },
    ]
    model = ItemCollection(**item_collection)
    links = model.model_dump()["links"]

    # assert False
    # Make sure we can mix links and pagination links
    normal_link = Link(**links[0])
    assert normal_link.rel == "self"
    next_link = PaginationLink(**links[2])
    assert next_link.rel == "next"
    previous_link = PaginationLink(**links[3])
    assert previous_link.rel == "prev"
    assert previous_link.body == {"key": "value"}


def test_resolve_pagination_link():
    normal_link = Link(href="/hello/world", type="image/jpeg", rel="test")
    page_link = PaginationLink(
        href="/next/page", type="image/jpeg", method="POST", rel="next"
    )
    links = Links.model_validate([normal_link, page_link])
    links.resolve(base_url="http://base_url.com")
    for link in links.link_iterator():
        if isinstance(link, PaginationLink):
            assert link.href == "http://base_url.com/next/page"


def test_link_types():
    for type_ in (MimeTypes.xml, "some random string", None):
        Link(href="/hello/world", type=type_, rel="test")
