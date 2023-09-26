import pytest
from pydantic import ValidationError

from stac_pydantic.api.search import ExtendedSearch


def test_api_sort_extension():
    ExtendedSearch(
        collections=["collection1", "collection2"],
        sortby=[
            {"field": "field1", "direction": "asc"},
            {"field": "field2", "direction": "desc"},
        ],
    )


def test_api_sort_extension_invalid():
    # Invalid sort direction
    with pytest.raises(ValidationError):
        ExtendedSearch(
            collections=["collection1", "collection2"],
            sortby=[{"field": "field1", "direction": "ascending"}],
        )
