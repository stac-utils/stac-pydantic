import pytest

from pydantic import BaseModel

from stac_pydantic import Collection, Item, ItemCollection, ItemProperties
from stac_pydantic.extensions import Extensions
from stac_pydantic.extensions.single_file_stac import SingleFileStac


@pytest.mark.parametrize(
    "infile",
    [
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/eo/examples/example-landsat8.json",
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/pointcloud/examples/example-autzen.json",
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/sat/examples/example-landsat8.json",
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/view/examples/example-landsat8.json",
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/scientific/examples/item.json",
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/datacube/examples/example-item.json",
    ],
)
def test_item_extensions(infile, request_test_data, test_equivalency):
    test_item = request_test_data(infile)
    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_sar_extensions(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/sar/examples/sentinel1.json"
    )

    # This example uses eo:bands instead of sar:polarizations for the measurement asset
    assert "sar:bands" in test_item["assets"]["measurement"]
    test_item["assets"]["measurement"]["sar:polarizations"] = test_item["assets"][
        "measurement"
    ].pop("sar:bands")

    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_proj_extension(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/projection/examples/example-landsat8.json"
    )

    # This example uses EO extension but doesn't include eo:gsd (required field)
    assert "eo" in test_item["stac_extensions"]
    assert "eo:gsd" not in test_item["properties"]
    test_item["properties"]["eo:gsd"] = 10

    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_version_extension_item(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/version/examples/item.json"
    )

    # This example adds version fields to top level of the feature instead of inside properties
    assert "version" in test_item
    test_item["properties"]["version"] = test_item.pop("version")

    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_version_extension_collection(request_test_data, test_equivalency):
    test_coll = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/version/examples/collection.json"
    )
    valid_coll = Collection(**test_coll).to_dict()
    test_equivalency(test_coll, valid_coll)

def test_collection_assets(request_test_data, test_equivalency):
    test_coll = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/asset/examples/example-landsat8.json"
    )
    # The example is missing links
    test_coll['links'] = [{
            "href": "mocked",
            "rel": "items"
        }
    ]
    valid_coll = Collection(**test_coll).to_dict()
    assert test_coll['assets'] == valid_coll['assets']

def test_label_extension(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/label/examples/spacenet-roads/roads_item.json"
    )

    # This example contains an invalid geometry (linear ring does not close)
    coords = test_item["geometry"]["coordinates"]
    assert len(coords[0]) == 4
    coords[0].append(coords[0][0])
    test_item["geometry"]["coordinates"] = coords

    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_commons_extension_collection(request_test_data, test_equivalency):
    test_coll = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/commons/examples/landsat-collection.json"
    )
    valid_coll = Collection(**test_coll).to_dict()
    test_equivalency(test_coll, valid_coll)


def test_explicit_extension_validation(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/eo/examples/example-landsat8.json"
    )

    # This item implements the eo and view extensions
    assert test_item["stac_extensions"][:-1] == ["eo", "view"]

    class ExtensionProperties(Extensions.eo, Extensions.view, ItemProperties):
        ...

    class CustomValidator(Item):
        properties: ExtensionProperties

    valid_item = CustomValidator(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_vendor_extension_validation(request_test_data, test_equivalency):
    test_item = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/eo/examples/example-landsat8.json"
    )

    # This item implements a vendor extension
    assert (
        test_item["stac_extensions"][-1]
        == "https://example.com/stac/landsat-extension/1.0/schema.json"
    )

    # Currently doesn't support remote extensions
    extension_id = "landsat"
    test_item["stac_extensions"][-1] = extension_id

    class LandsatExtension(BaseModel):
        path: int
        row: int

        class Config:
            allow_population_by_fieldname = True
            alias_generator = lambda field_name: f"landsat:{field_name}"

    Extensions.register(extension_id, LandsatExtension)

    valid_item = Item(**test_item).to_dict()
    test_equivalency(test_item, valid_item)


def test_item_collection(request_test_data, test_equivalency):
    test_item_coll = request_test_data(
        "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/item-spec/examples/itemcollection-sample-full.json"
    )

    valid_item_coll = ItemCollection(**test_item_coll).to_dict()
    for idx, feat in enumerate(test_item_coll["features"]):
        test_equivalency(feat, valid_item_coll["features"][idx])
