import json
import time
from datetime import datetime, timezone

import pytest
from pydantic import Field, ValidationError
from shapely.geometry import shape

from stac_pydantic import Catalog, Collection, Item, ItemCollection, ItemProperties
from stac_pydantic.api import Collections
from stac_pydantic.api.conformance import ConformanceClasses
from stac_pydantic.api.landing import LandingPage
from stac_pydantic.api.search import Search
from stac_pydantic.extensions import validate_extensions
from stac_pydantic.links import Link, Links, PaginationLink
from stac_pydantic.shared import DATETIME_RFC339
from stac_pydantic.version import STAC_VERSION

from .conftest import dict_match, request

COLLECTION = "landsat-collection.json"
ITEM_COLLECTION = "itemcollection-sample-full.json"
SINGLE_FILE_STAC = "example-search.json"

# ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/asset/examples/example-landsat8.json"
# COLLECTION_ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions/collection-assets/examples/example-esm.json"
DATACUBE_EXTENSION = "example-item_datacube-extension.json"
EO_EXTENSION = "example-landsat8_eo-extension.json"
ITEM_ASSET_EXTENSION = "example-landsat8_item-assets-extension.json"
LABEL_EXTENSION = "roads_item.json"
POINTCLOUD_EXTENSION = "example-autzen.json"
PROJ_EXTENSION = "example-landsat8_projection-extension.json"
SAR_EXTENSION = "sentinel1_sar-extension.json"
SAT_EXTENSION = "example-landsat8_sat-extension.json"
SCIENTIFIC_EXTENSION = "example-item_sci-extension.json"
VERSION_EXTENSION_ITEM = "example-item_version-extension.json"
VERSION_EXTENSION_COLLECTION = "example-collection_version-extension.json"
VIEW_EXTENSION = "example-landsat8_view-extension.json"
DATETIME_RANGE = "datetimerange.json"
EXAMPLE_COLLECTION_LIST = "example-collection-list.json"


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
    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_sar_extensions():
    test_item = request(SAR_EXTENSION)
    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_proj_extension():
    # The example item uses an invalid band name
    test_item = request(PROJ_EXTENSION)
    test_item["stac_extensions"][
        1
    ] = "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json"
    test_item["assets"]["B8"]["eo:bands"][0]["common_name"] = "pan"

    valid_item = Item.parse_obj(test_item).to_dict()
    dict_match(test_item, valid_item)


def test_version_extension_item():
    test_item = request(VERSION_EXTENSION_ITEM)
    valid_item = Item(**test_item).to_dict()
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

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_explicit_extension_validation():
    test_item = request(EO_EXTENSION)

    # This item implements the eo and view extensions
    assert test_item["stac_extensions"][:-1] == [
        "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
        "https://stac-extensions.github.io/view/v1.0.0/schema.json",
    ]

    validate_extensions(test_item)


def test_item_collection():
    test_item_coll = request(ITEM_COLLECTION)
    test_item_coll["stac_version"] = STAC_VERSION
    for feat in test_item_coll["features"]:
        feat["stac_version"] = STAC_VERSION

    valid_item_coll = ItemCollection(**test_item_coll).to_dict()
    for idx, feat in enumerate(test_item_coll["features"]):
        dict_match(feat, valid_item_coll["features"][idx])


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
    dict_match(json.loads(validated.to_json()), validated.to_dict())


def test_item_to_json():
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    dict_match(json.loads(item.to_json()), item.to_dict())


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
        id="test-landing-page",
        description="stac-api landing page",
        stac_extensions=[
            "https://raw.githubusercontent.com/stac-extensions/eo/v1.0.0/json-schema/schema.json",
            "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json",
        ],
        conformsTo=[
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ],
        links=[Link(href="http://link", rel="self",)],
    )


def test_api_landing_page_is_catalog():
    landing_page = LandingPage(
        id="test-landing-page",
        description="stac-api landing page",
        stac_extensions=[
            "https://raw.githubusercontent.com/stac-extensions/eo/v1.0.0/json-schema/schema.json",
            "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json",
        ],
        conformsTo=[
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ],
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

    # Search GeometryCollection
    search = Search(
        collections=["collection1", "collection2"],
        intersects={
            "type": "GeometryCollection", 
            "geometries": [
                {"type": "Point", "coordinates": [0, 0]}
            ]
        },
    )


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


def test_temporal_search_single_tailed():
    # Test single tailed
    utcnow = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
    utcnow_str = utcnow.strftime(DATETIME_RFC339)
    search = Search(collections=["collection1"], datetime=utcnow_str)
    assert search.start_date == None
    assert search.end_date == utcnow


def test_temporal_search_two_tailed():
    # Test two tailed
    utcnow = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
    utcnow_str = utcnow.strftime(DATETIME_RFC339)
    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/{utcnow_str}")
    assert search.start_date == search.end_date == utcnow

    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/..")
    assert search.start_date == utcnow
    assert search.end_date == None


def test_temporal_search_open():
    # Test open date range
    search = Search(collections=["collection1"], datetime="../..")
    assert search.start_date == search.end_date == None


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

    model = TestItem(**test_item)
    assert model.properties.foo == "bar"


def test_serialize_namespace():
    test_item = request(SAR_EXTENSION)
    valid_item = Item(**test_item)
    assert "sar:instrument_mode" in valid_item.dict()["properties"]


def test_excludes():
    test_item = request(EO_EXTENSION)
    valid_item = Item(**test_item).dict(
        by_alias=True, exclude_unset=True, exclude={"properties": {"bands"}}
    )
    assert "eo:bands" not in valid_item["properties"]


def test_validate_extensions():
    test_item = request(SAR_EXTENSION)
    assert validate_extensions(test_item)


def test_validate_extensions_reraise_exception():
    test_item = request(EO_EXTENSION)
    del test_item["properties"]["datetime"]

    with pytest.raises(ValidationError):
        Item.parse_obj(test_item)
        validate_extensions(test_item, reraise_exception=True)


def test_validate_extensions_rfc3339_with_partial_seconds():
    test_item = request(SAR_EXTENSION)
    test_item["properties"]["updated"] = "2018-10-01T01:08:32.033Z"
    assert validate_extensions(test_item)


@pytest.mark.parametrize("url,cls", [[EO_EXTENSION, Item], [COLLECTION, Collection]])
def test_extension(url, cls):
    test_data = request(url)
    test_data["stac_extensions"].append("https://foo")
    model = cls.parse_obj(test_data)
    assert "https://foo" in model.stac_extensions


def test_resolve_link():
    link = Link(href="/hello/world", type="image/jpeg", rel="test")
    link.resolve(base_url="http://base_url.com")
    assert link.href == "http://base_url.com/hello/world"


def test_resolve_links():
    links = Links.parse_obj([Link(href="/hello/world", type="image/jpeg", rel="test")])
    links.resolve(base_url="http://base_url.com")
    for link in links:
        assert link.href == "http://base_url.com/hello/world"


def test_resolve_pagination_link():
    normal_link = Link(href="/hello/world", type="image/jpeg", rel="test")
    page_link = PaginationLink(
        href="/next/page", type="image/jpeg", method="POST", rel="next"
    )
    links = Links.parse_obj([normal_link, page_link])
    links.resolve(base_url="http://base_url.com")
    for link in links:
        if isinstance(link, PaginationLink):
            assert link.href == "http://base_url.com/next/page"


def test_collection_list():
    test_collection_list = request(EXAMPLE_COLLECTION_LIST)
    valid_collection_list = Collections(**test_collection_list).to_dict()
    dict_match(test_collection_list, valid_collection_list)
