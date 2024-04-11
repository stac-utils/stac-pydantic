import pytest
from pydantic import ValidationError

from stac_pydantic.api.search import ExtendedSearch, Search


def test_api_query_extension():
    # One field
    Search(collections=["collection1", "collection2"], query={"field": {"lt": 100}})

    # Many fields
    Search(
        collections=["collection1", "collection2"],
        query={"field": {"lt": 100}, "field1": {"gt": 200}},
    )


def test_api_query_extension_invalid():
    # Invalid operator
    with pytest.raises(ValidationError):
        ExtendedSearch(
            collections=["collection1", "collection2"],
            query={"field": {"greater_than": 100}},
        )
