from stac_pydantic.api import Collections
from stac_pydantic.api.version import STAC_API_VERSION

from ..conftest import dict_match, request

EXAMPLE_COLLECTION_LIST = "example-collection-list.json"
PATH = ["tests", "api", "examples", f"v{STAC_API_VERSION}"]


def test_collection_list():
    test_collection_list = request(EXAMPLE_COLLECTION_LIST, PATH)
    valid_collection_list = Collections(**test_collection_list).model_dump(mode="json")
    dict_match(test_collection_list, valid_collection_list)
