import json

from stac_pydantic import ItemCollection
from stac_pydantic.version import STAC_VERSION

from .conftest import dict_match, request

ITEM_COLLECTION = "itemcollection-sample-full.json"
PATH = ["tests", "example_stac"]


def test_item_collection():
    test_item_coll = request(ITEM_COLLECTION, PATH)

    for feat in test_item_coll["features"]:
        feat["stac_version"] = STAC_VERSION

    valid_item_coll = ItemCollection(**test_item_coll).model_dump()
    for idx, feat in enumerate(test_item_coll["features"]):
        dict_match(feat, valid_item_coll["features"][idx])


def test_to_json():
    test_item = request(ITEM_COLLECTION, PATH)
    for feat in test_item["features"]:
        feat["stac_version"] = STAC_VERSION

    validated = ItemCollection(**test_item)
    dict_match(json.loads(validated.model_dump_json()), validated.model_dump())
