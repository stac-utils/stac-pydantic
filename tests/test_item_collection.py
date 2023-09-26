import json

from stac_pydantic import ItemCollection
from stac_pydantic.api.version import STAC_API_VERSION
from stac_pydantic.version import STAC_VERSION

from .conftest import dict_match, request

ITEM_COLLECTION = "itemcollection-sample-full.json"
PATH = ["tests", "api", "examples", f"v{STAC_API_VERSION}"]

# TODO sort this out. has extra attributes but missing links
# @pytest.mark.parametrize("example_url", [f"https://raw.githubusercontent.com/radiantearth/stac-api-spec/v{STAC_API_VERSION}/fragments/itemcollection/examples/itemcollection-sample-full.json",
#                                          f"https://raw.githubusercontent.com/radiantearth/stac-api-spec/v{STAC_API_VERSION}/fragments/itemcollection/examples/itemcollection-sample-minimal.json"])
# def test_item_collection_examples(example_url):
#     """
#     Testing the less strict version here, not enforcing required Links
#     """
#     compare_example(example_url, ItemCollection)


def test_item_collection():
    test_item_coll = request(ITEM_COLLECTION, PATH)
    # test_item_coll["stac_version"] = STAC_VERSION
    for feat in test_item_coll["features"]:
        feat["stac_version"] = STAC_VERSION

    valid_item_coll = ItemCollection(**test_item_coll).model_dump()
    for idx, feat in enumerate(test_item_coll["features"]):
        dict_match(feat, valid_item_coll["features"][idx])


# TODO: REFACTOR
def test_to_json():
    test_item = request(ITEM_COLLECTION, PATH)
    for feat in test_item["features"]:
        feat["stac_version"] = STAC_VERSION

    validated = ItemCollection(**test_item)
    dict_match(json.loads(validated.model_dump_json()), validated.model_dump())
