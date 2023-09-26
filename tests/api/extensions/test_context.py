import jsonschema
import pytest
import requests
from pydantic import ValidationError

from stac_pydantic.api.extensions.context import CONTEXT_VERSION, ContextExtension
from stac_pydantic.api.item_collection import ItemCollection
from stac_pydantic.api.version import STAC_API_VERSION
from stac_pydantic.version import STAC_VERSION

from ...conftest import request

ITEM_COLLECTION = "itemcollection-sample-full.json"
PATH = ["tests", "api", "examples", f"v{STAC_API_VERSION}"]


valid_context = [
    (10, 10, 10),
    (10, 20, 30),
    (10, 10, None),
    (10, None, None),
]
invalid_context = [
    (10, 1, 1),
    (10, None, 1),
    (20, 10, None),
    (None, 10, 10),
]


@pytest.mark.parametrize("returned,limit,matched", valid_context)
def test_context_extension(returned, limit, matched):
    context = {"returned": returned, "limit": limit, "matched": matched}

    result = ContextExtension(**context).model_dump()
    assert result == context


@pytest.mark.parametrize("returned,limit,matched", valid_context)
def test_context_schema(returned, limit, matched):
    schema_url = f"https://github.com/stac-api-extensions/context/blob/{CONTEXT_VERSION}/json-schema/schema.json"
    req = requests.get(schema_url)
    schema = req.json()

    context = {"returned": returned, "limit": limit, "matched": matched}

    jsonschema.validate(instance=context, schema=schema)


@pytest.mark.parametrize("returned,limit,matched", invalid_context)
def test_context_extension_invalid(returned, limit, matched):
    context = {"returned": returned, "limit": limit, "matched": matched}

    with pytest.raises((ValueError, TypeError)):
        ContextExtension(**context).model_dump()


def test_api_item_collection_with_context_extension():
    item_collection = request(ITEM_COLLECTION, PATH)
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION

    item_collection["context"] = {"returned": 10, "limit": 10, "matched": 100}
    ItemCollection(**item_collection)


def test_api_context_extension_invalid():
    item_collection = request(ITEM_COLLECTION, PATH)
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION

    item_collection.update({"context": {"returned": 20, "limit": 10, "matched": 100}})

    with pytest.raises(ValidationError):
        ItemCollection(**item_collection)
