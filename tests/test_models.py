import json
import time
from datetime import datetime

import pytest
from pydantic import BaseModel, Field, ValidationError
from shapely.geometry import shape

from stac_pydantic import Catalog, Collection, Item, ItemCollection, ItemProperties
from stac_pydantic.api.conformance import ConformanceClasses
from stac_pydantic.api.extensions.paging import PaginationLink
from stac_pydantic.api.landing import LandingPage
from stac_pydantic.api.search import Search
from stac_pydantic.extensions import Extensions
from stac_pydantic.extensions.single_file_stac import SingleFileStac
from stac_pydantic.item import item_model_factory, validate_item
from stac_pydantic.shared import DATETIME_RFC339, Link
from stac_pydantic.version import STAC_VERSION

from .conftest import dict_match, request


class LandsatExtension(BaseModel):
    path: int = Field(..., alias="landsat:path")
    row: int = Field(..., alias="landsat:row")

    class Config:
        allow_population_by_fieldname = True


landsat_alias = "https://example.com/stac/landsat-extension/1.0/schema.json"
Extensions.register("landsat", LandsatExtension, alias=landsat_alias)

COLLECTION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/collection-spec/examples/landsat-collection.json"
ITEM_COLLECTION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/item-spec/examples/itemcollection-sample-full.json"
SINGLE_FILE_STAC = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/single-file-stac/examples/example-search.json"

# ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/asset/examples/example-landsat8.json"
# COLLECTION_ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/collection-assets/examples/example-esm.json"
DATACUBE_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/datacube/examples/example-item.json"
EO_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/eo/examples/example-landsat8.json"
ITEM_ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0-beta.2/extensions/item-assets/examples/example-landsat8.json"
LABEL_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/label/examples/spacenet-roads/roads_item.json"
POINTCLOUD_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/pointcloud/examples/example-autzen.json"
PROJ_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/projection/examples/example-landsat8.json"
SAR_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/sar/examples/sentinel1.json"
SAT_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/sat/examples/example-landsat8.json"
SCIENTIFIC_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/scientific/examples/item.json"
VERSION_EXTENSION_ITEM = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/version/examples/item.json"
VERSION_EXTENSION_COLLECTION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/version/examples/collection.json"
VIEW_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/view/examples/example-landsat8.json"
DATETIME_RANGE = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/item-spec/examples/datetimerange.json"


@pytest.mark.parametrize(
    "infile",
    [
        EO_EXTENSION,
        POINTCLOUD_EXTENSION,
        SAT_EXTENSION,
        VIEW_EXTENSION,
        SCIENTIFIC_EXTENSION,
        DATACUBE_EXTENSION,
        DATETIME_RANGE,
    ],
)
def test_item_extensions(infile):
    test_item = request(infile)
    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_sar_extensions():
    test_item = request(SAR_EXTENSION)
    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_proj_extension():
    # The example item uses an invalid band name
    test_item = request(PROJ_EXTENSION)
    test_item["stac_extensions"][1] = "projection"
    test_item["assets"]["B8"]["eo:bands"][0]["common_name"] = "pan"

    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_version_extension_item():
    test_item = request(VERSION_EXTENSION_ITEM)
    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_version_extension_collection():
    test_coll = request(VERSION_EXTENSION_COLLECTION)
    valid_coll = Collection(**test_coll).to_dict()
    dict_match(test_coll, valid_coll)


def test_item_assets_extension():
    test_coll = request(ITEM_ASSET_EXTENSION)
    valid_coll = Collection(**test_coll).to_dict()
    dict_match(test_coll, valid_coll)


def test_label_extension():
    test_item = request(LABEL_EXTENSION)

    # This example contains an invalid geometry (linear ring does not close)
    coords = test_item["geometry"]["coordinates"]
    assert len(coords[0]) == 4
    coords[0].append(coords[0][0])
    test_item["geometry"]["coordinates"] = coords

    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_explicit_extension_validation():
    test_item = request(EO_EXTENSION)

    # This item implements the eo and view extensions
    assert test_item["stac_extensions"][:-1] == ["eo", "view"]

    class ExtensionProperties(Extensions.eo, Extensions.view, ItemProperties):
        ...

    class CustomValidator(Item):
        properties: ExtensionProperties

    valid_item = CustomValidator(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_vendor_extension_validation():
    test_item = request(EO_EXTENSION)

    # This item implements a vendor extension
    assert (
        test_item["stac_extensions"][-1]
        == "https://example.com/stac/landsat-extension/1.0/schema.json"
    )

    test_item["stac_extensions"][-1] = landsat_alias

    valid_item = item_model_factory(test_item)(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_vendor_extension_invalid_alias():
    url = "https://invalid-url"
    test_item = request(EO_EXTENSION)
    test_item["stac_extensions"][-1] = url

    with pytest.raises(AttributeError) as e:
        model = item_model_factory(test_item)
    assert str(e.value) == f"Invalid extension name or alias: {url}"


def test_item_collection():
    test_item_coll = request(ITEM_COLLECTION)
    test_item_coll["stac_version"] = STAC_VERSION
    for feat in test_item_coll["features"]:
        feat["stac_version"] = STAC_VERSION

    valid_item_coll = ItemCollection(**test_item_coll).to_dict()
    for idx, feat in enumerate(test_item_coll["features"]):
        dict_match(feat, valid_item_coll["features"][idx])


def test_single_file_stac():
    test_sfs = request(SINGLE_FILE_STAC)
    # item collection is missing stac version and links
    test_sfs["links"] = [{"type": "fake", "href": "http://mocked.com", "rel": "fake"}]

    # collection extents are from an older stac version
    for coll in test_sfs["collections"]:
        coll["stac_extensions"][0] = "projection"

    for feat in test_sfs["features"]:
        feat["stac_extensions"][0] = "projection"

    valid_sfs = SingleFileStac(**test_sfs).to_dict()

    for idx, feat in enumerate(test_sfs["features"]):
        dict_match(feat, valid_sfs["features"][idx])

    for idx, feat in enumerate(test_sfs["collections"]):
        dict_match(feat, valid_sfs["collections"][idx])


@pytest.mark.parametrize(
    "infile,model",
    [(EO_EXTENSION, Item), (ITEM_COLLECTION, ItemCollection), (COLLECTION, Collection)],
)
def test_to_json(infile, model):
    test_item = request(infile)

    if issubclass(model, ItemCollection):
        test_item["stac_version"] = STAC_VERSION
        for feat in test_item["features"]:
            feat["stac_version"] = STAC_VERSION

    validated = model(**test_item)
    assert validated.to_json() == json.dumps(validated.to_dict())


def test_item_to_json():
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    assert item.to_json() == json.dumps(item.to_dict())


def test_datacube_extension_validation_error():
    test_item = request(DATACUBE_EXTENSION)
    test_item["properties"]["cube:dimensions"]["x"]["extent"] = ""

    model = item_model_factory(test_item)
    with pytest.raises(ValidationError):
        model(**test_item)


def test_eo_extension_validation_error():
    test_item = request(EO_EXTENSION)
    test_item["properties"]["eo:cloud_cover"] = "foo"
    model = item_model_factory(test_item)
    with pytest.raises(ValidationError):
        model(**test_item)


def test_label_extension_validation_error():
    test_item = request(LABEL_EXTENSION)
    test_item["properties"]["label:type"] = "invalid-label-type"

    with pytest.raises(ValidationError):
        Item(**test_item)


def test_point_cloud_extension_validation_error():
    test_item = request(POINTCLOUD_EXTENSION)
    test_item["properties"]["pc:count"] = ["not-an-int"]
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_proj_extension_validation_error():
    test_item = request(PROJ_EXTENSION)
    test_item["stac_extensions"][1] = "projection"
    del test_item["properties"]["proj:epsg"]
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_sar_extension_validation_error():
    test_item = request(SAR_EXTENSION)
    test_item["properties"]["sar:polarizations"] = ["foo", "bar"]
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_sci_extension_validation_error():
    test_item = request(SCIENTIFIC_EXTENSION)
    test_item["properties"]["sci:doi"] = [43]
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_single_file_stac_validation_error():
    test_item = request(SINGLE_FILE_STAC)
    del test_item["collections"]

    with pytest.raises(ValidationError):
        Item(**test_item)


def test_version_extension_validation_error():
    test_item = request(VERSION_EXTENSION_ITEM)
    del test_item["properties"]["version"]
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_view_extension_validation_error():
    test_item = request(VIEW_EXTENSION)
    test_item["properties"]["view:off_nadir"] = "foo"
    model = item_model_factory(test_item)

    with pytest.raises(ValidationError):
        model(**test_item)


def test_invalid_geometry():
    test_item = request(EO_EXTENSION)

    # Remove the last coordinate
    test_item["geometry"]["coordinates"][0].pop(-1)

    with pytest.raises(ValidationError) as e:
        Item(**test_item)


def test_asset_extras():
    test_item = request(EO_EXTENSION)
    for asset in test_item["assets"]:
        test_item["assets"][asset]["foo"] = "bar"

    item = Item(**test_item)
    for (asset_name, asset) in item.assets.items():
        assert asset.foo == "bar"


def test_geo_interface():
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    geom = shape(item.geometry)
    test_item["geometry"] = geom
    Item(**test_item)


def test_api_conformance():
    ConformanceClasses(
        conformsTo=["https://conformance-class-1", "http://conformance-class-2"]
    )


def test_api_conformance_invalid_url():
    with pytest.raises(ValidationError):
        ConformanceClasses(conformsTo=["s3://conformance-class"])


def test_api_landing_page():
    LandingPage(
        id='test-landing-page',
        description="stac-api landing page",
        stac_extensions=["eo", "proj"],
        links=[Link(href="http://link", rel="self",)],
    )

def test_api_landing_page_is_catalog():
    landing_page = LandingPage(
        id='test-landing-page',
        description="stac-api landing page",
        stac_extensions=["eo", "proj"],
        links=[Link(href="http://link", rel="self",)],
    )
    catalog = Catalog(**landing_page.dict())


def test_search():
    Search(collections=["collection1", "collection2"])


def test_search_by_id():
    Search(collections=["collection1", "collection2"], ids=["id1", "id2"])


def test_spatial_search():
    # Search with bbox
    Search(collections=["collection1", "collection2"], bbox=[-180, -90, 180, 90])

    # Search with geojson
    search = Search(
        collections=["collection1", "collection2"],
        intersects={"type": "Point", "coordinates": [0, 0]},
    )
    shape(search.intersects)


def test_invalid_spatial_search():
    # bbox and intersects are mutually exclusive
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            intersects={"type": "Point", "coordinates": [0, 0]},
            bbox=[-180, -90, 180, 90],
        )

    # Invalid geojson
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            intersects={"type": "Polygon", "coordinates": [0]},
        )


def test_temporal_search():
    # Test single tailed
    utcnow = datetime.utcnow().strftime(DATETIME_RFC339)
    search = Search(collections=["collection1"], datetime=utcnow)
    assert len(search.datetime) == 2
    assert search.datetime == ["..", utcnow]

    # Test two tailed
    search = Search(collections=["collection1"], datetime=f"{utcnow}/{utcnow}")
    assert len(search.datetime) == 2
    assert search.datetime == [utcnow, utcnow]

    search = Search(collections=["collection1"], datetime=f"{utcnow}/..")
    assert len(search.datetime) == 2
    assert search.datetime == [utcnow, ".."]

    # Test open date range
    search = Search(collections=["collection1"], datetime=f"../..")
    assert len(search.datetime) == 2
    assert search.datetime == ["..", ".."]


def test_invalid_temporal_search():
    # Not RFC339
    utcnow = datetime.utcnow().strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        search = Search(collections=["collection1"], datetime=utcnow)

    # End date is before start date
    start = datetime.utcnow()
    time.sleep(2)
    end = datetime.utcnow()
    with pytest.raises(ValidationError):
        search = Search(
            collections=["collection1"],
            datetime=f"{end.strftime(DATETIME_RFC339)}/{start.strftime(DATETIME_RFC339)}",
        )


def test_api_context_extension():
    item_collection = request(ITEM_COLLECTION)
    item_collection["stac_version"] = STAC_VERSION
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION

    item_collection.update({"context": {"returned": 10, "limit": 10, "matched": 100}})
    ItemCollection(**item_collection)


def test_api_context_extension_invalid():
    item_collection = request(ITEM_COLLECTION)
    item_collection["stac_version"] = STAC_VERSION
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION

    item_collection.update({"context": {"returned": 20, "limit": 10, "matched": 100}})

    with pytest.raises(ValidationError):
        ItemCollection(**item_collection)


def test_api_fields_extension():
    Search(
        collections=["collection1"],
        fields={"includes": {"field1", "field2"}, "excludes": {"field3", "field4"}},
    )


def test_api_paging_extension():
    item_collection = request(ITEM_COLLECTION)
    item_collection["stac_version"] = STAC_VERSION
    for feat in item_collection["features"]:
        feat["stac_version"] = STAC_VERSION
    item_collection["links"] += [
        {"title": "next page", "rel": "next", "method": "GET", "href": "http://next"},
        {
            "title": "previous page",
            "rel": "previous",
            "method": "POST",
            "href": "http://prev",
            "body": {"key": "value"},
        },
    ]
    model = ItemCollection(**item_collection)
    links = model.to_dict()["links"]

    # Make sure we can mix links and pagination links
    normal_link = Link(**links[0])
    assert normal_link.rel == "self"
    next_link = PaginationLink(**links[1])
    assert next_link.rel == "next"
    previous_link = PaginationLink(**links[2])
    assert previous_link.rel == "previous"
    assert previous_link.body == {"key": "value"}


def test_api_invalid_paging_link():
    # Invalid rel type
    with pytest.raises(ValidationError):
        PaginationLink(rel="self", method="GET", href="http://next")

    # Invalid method
    with pytest.raises(ValidationError):
        PaginationLink(rel="next", method="DELETE", href="http://next")


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
        Search(
            collections=["collection1", "collection2"],
            query={"field": {"greater_than": 100}},
        )


def test_api_sort_extension():
    Search(
        collections=["collection1", "collection2"],
        sortby=[
            {"field": "field1", "direction": "asc"},
            {"field": "field2", "direction": "desc"},
        ],
    )


def test_api_sort_extension_invalid():
    # Invalid sort direction
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            sortby=[{"field": "field1", "direction": "ascending"}],
        )


def test_declared_model():
    class TestProperties(ItemProperties):
        foo: str
        bar: int

        class Config:
            allow_population_by_fieldname = True
            alias_generator = lambda field_name: f"test:{field_name}"

    class TestItem(Item):
        properties: TestProperties

    test_item = request(EO_EXTENSION)
    del test_item["stac_extensions"]
    test_item["properties"] = {
        "datetime": test_item["properties"]["datetime"],
        "test:foo": "mocked",
        "test:bar": 1,
    }

    valid_item = TestItem(**test_item).to_dict()

    assert "test:foo" in valid_item["properties"]
    assert "test:bar" in valid_item["properties"]


def test_item_factory_custom_base():
    class TestProperties(ItemProperties):
        foo: str = Field("bar", const=True)

    class TestItem(Item):
        properties: TestProperties

    test_item = request(EO_EXTENSION)

    model = item_model_factory(test_item, base_class=TestItem)(**test_item)
    assert model.properties.foo == "bar"


def test_serialize_namespace():
    test_item = request(SAR_EXTENSION)
    valid_item = item_model_factory(test_item)(**test_item)
    assert "sar:instrument_mode" in valid_item.dict(by_alias=True)["properties"]
    assert "instrument_mode" in valid_item.dict(by_alias=False)["properties"]


def test_excludes():
    test_item = request(EO_EXTENSION)
    valid_item = item_model_factory(test_item)(**test_item).dict(
        by_alias=True, exclude_unset=True, exclude={"properties": {"bands"}}
    )
    assert "eo:bands" not in valid_item["properties"]


def test_register_extension():
    class TestExtension(BaseModel):
        foo: str
        bar: int

    Extensions.register("test", TestExtension, alias="test_extension")

    assert Extensions.get("test") == Extensions.get("test-extension") == TestExtension


def test_get_missing_extension():
    with pytest.raises(AttributeError):
        Extensions.get("not-an-extension")


def test_skip_remote_extension():
    test_item = request(EO_EXTENSION)
    test_item["stac_extensions"].append("http://some-remote-extension.json.schema")

    # This should fail
    with pytest.raises(AttributeError):
        item_model_factory(test_item, skip_remote_refs=False)(**test_item)

    # This should work
    item_model_factory(test_item, skip_remote_refs=True)(**test_item)


def test_validate_item():
    test_item = request(EO_EXTENSION)
    assert validate_item(test_item)


def test_validate_item_reraise_exception():
    test_item = request(EO_EXTENSION)
    del test_item["properties"]["datetime"]

    with pytest.raises(ValidationError):
        validate_item(test_item, reraise_exception=True)


def test_multi_inheritance():
    test_item = request(EO_EXTENSION)

    class TestProperties(
        LandsatExtension, Extensions.eo, Extensions.view, ItemProperties
    ):
        ...

    properties = TestProperties(**test_item["properties"]).dict(by_alias=True)
    assert "datetime" in properties
    assert "gsd" in properties
    assert "view:off_nadir" in properties
    assert "landsat:path" in properties


@pytest.mark.parametrize("url,cls", [[EO_EXTENSION, Item], [COLLECTION, Collection]])
def test_extension(url, cls):
    test_data = request(url)
    test_data["stac_extensions"].append("foo")
    model = cls.parse_obj(test_data)
    assert "foo" in model.stac_extensions
