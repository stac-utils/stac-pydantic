from datetime import datetime
import json
import time

import pytest
from pydantic import BaseModel, ValidationError
from shapely.geometry import shape

from stac_pydantic import Collection, Item, ItemCollection, ItemProperties
from stac_pydantic.shared import Link, DATETIME_RFC339
from stac_pydantic.api.conformance import ConformanceClasses
from stac_pydantic.api.landing import LandingPage
from stac_pydantic.api.search import Search
from stac_pydantic.api.extensions.paging import PaginationLink
from stac_pydantic.extensions import Extensions
from stac_pydantic.extensions.single_file_stac import SingleFileStac


from .conftest import dict_match, request

class LandsatExtension(BaseModel):
    path: int
    row: int

    class Config:
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"landsat:{field_name}"


landsat_alias = "https://example.com/stac/landsat-extension/1.0/schema.json"
Extensions.register("landsat", LandsatExtension, alias=landsat_alias)

COLLECTION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/collection-spec/examples/landsat-collection.json"
ITEM_COLLECTION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/item-spec/examples/itemcollection-sample-full.json"
SINGLE_FILE_STAC = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/single-file-stac/examples/example-search.json"

ASSET_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/asset/examples/example-landsat8.json"
COMMONS_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/commons/examples/landsat-collection.json"
DATACUBE_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/datacube/examples/example-item.json"
EO_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/eo/examples/example-landsat8.json"
LABEL_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/label/examples/spacenet-roads/roads_item.json"
POINTCLOUD_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/pointcloud/examples/example-autzen.json"
PROJ_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/projection/examples/example-landsat8.json"
SAR_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/sar/examples/sentinel1.json"
SAT_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/sat/examples/example-landsat8.json"
SCIENTIFIC_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/scientific/examples/item.json"
VERSION_EXTENSION_ITEM = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/version/examples/item.json"
VERSION_EXTENSION_COLLECTION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/version/examples/collection.json"
VIEW_EXTENSION = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/extensions/view/examples/example-landsat8.json"

DATETIME_RANGE = "https://raw.githubusercontent.com/radiantearth/stac-spec/v0.9.0/item-spec/examples/datetimerange.json"

@pytest.mark.parametrize(
    "infile",
    [
        EO_EXTENSION,
        POINTCLOUD_EXTENSION,
        SAT_EXTENSION,
        VIEW_EXTENSION,
        SCIENTIFIC_EXTENSION,
        DATACUBE_EXTENSION,
        DATETIME_RANGE
    ],
)
def test_item_extensions(infile):
    test_item = request(infile)
    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_sar_extensions():
    test_item = request(SAR_EXTENSION)

    # This example uses eo:bands instead of sar:polarizations for the measurement asset
    assert "sar:bands" in test_item["assets"]["measurement"]
    test_item["assets"]["measurement"]["sar:polarizations"] = test_item["assets"][
        "measurement"
    ].pop("sar:bands")

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_proj_extension():
    test_item = request(PROJ_EXTENSION)

    # This example uses EO extension but doesn't include eo:gsd (required field)
    assert "eo" in test_item["stac_extensions"]
    assert "eo:gsd" not in test_item["properties"]
    test_item["properties"]["eo:gsd"] = 10

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_version_extension_item():
    test_item = request(VERSION_EXTENSION_ITEM)

    # This example adds version fields to top level of the feature instead of inside properties
    assert "version" in test_item
    test_item["properties"]["version"] = test_item.pop("version")

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_version_extension_collection():
    test_coll = request(VERSION_EXTENSION_COLLECTION)
    valid_coll = Collection(**test_coll).to_dict()
    dict_match(test_coll, valid_coll)


def test_collection_assets():
    test_coll = request(ASSET_EXTENSION)
    # The example is missing links
    test_coll["links"] = [{"href": "mocked", "rel": "items"}]
    valid_coll = Collection(**test_coll).to_dict()
    assert test_coll["assets"] == valid_coll["assets"]


def test_label_extension():
    test_item = request(LABEL_EXTENSION)

    # This example contains an invalid geometry (linear ring does not close)
    coords = test_item["geometry"]["coordinates"]
    assert len(coords[0]) == 4
    coords[0].append(coords[0][0])
    test_item["geometry"]["coordinates"] = coords

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_commons_extension_collection():
    test_coll = request(COMMONS_EXTENSION)
    valid_coll = Collection(**test_coll).to_dict()
    dict_match(test_coll, valid_coll)


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

    valid_item = Item(**test_item).to_dict()
    dict_match(test_item, valid_item)


def test_vendor_extension_invalid_alias():
    url = "https://invalid-url"
    test_item = request(EO_EXTENSION)
    test_item["stac_extensions"][-1] = url

    with pytest.raises(AttributeError) as e:
        Item(**test_item)
    assert str(e.value) == f"Invalid extension name or alias: {url}"


def test_item_collection():
    test_item_coll = request(ITEM_COLLECTION)

    valid_item_coll = ItemCollection(**test_item_coll).to_dict()
    for idx, feat in enumerate(test_item_coll["features"]):
        dict_match(feat, valid_item_coll["features"][idx])


def test_single_file_stac():
    test_sfs = request(SINGLE_FILE_STAC)
    # item collection is missing stac version and links
    test_sfs["stac_version"] = "0.9.0"
    test_sfs["links"] = [{"type": "fake", "href": "http://mocked.com", "rel": "fake"}]

    # items are missing stac version
    for item in test_sfs["features"]:
        item["stac_version"] = "0.9.0"

    # collection extents are from an older stac version
    for coll in test_sfs["collections"]:
        coll["extent"]["spatial"] = {"bbox": [coll["extent"]["spatial"]]}
        coll["extent"]["temporal"] = {"interval": [coll["extent"]["temporal"]]}
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
    validated = model(**test_item)
    assert validated.to_json() == json.dumps(validated.to_dict())


def test_item_to_json():
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    assert item.to_json() == json.dumps(item.to_dict())


def test_assets_extension_validation_error():
    test_collection = request(ASSET_EXTENSION)
    del test_collection["assets"]

    with pytest.raises(ValidationError):
        Collection(**test_collection)


def test_commons_extension_validation_error():
    test_collection = request(COMMONS_EXTENSION)
    del test_collection["properties"]

    with pytest.raises(ValidationError):
        Collection(**test_collection)


def test_datacube_extension_validation_error():
    test_item = request(DATACUBE_EXTENSION)
    test_item["properties"]["cube:dimensions"]["x"]["extent"] = ""

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_eo_extension_validation_error():
    test_item = request(EO_EXTENSION)
    del test_item["properties"]["eo:bands"]
    with pytest.raises(ValidationError):
        Item(**test_item)


def test_label_extension_validation_error():
    test_item = request(LABEL_EXTENSION)
    test_item["properties"]["label:type"] = "invalid-label-type"

    with pytest.raises(ValidationError):
        Item(**test_item)


def test_point_cloud_extension_validation_error():
    test_item = request(POINTCLOUD_EXTENSION)
    test_item["properties"]["pc:count"] = ["not-an-int"]

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_proj_extension_validation_error():
    test_item = request(PROJ_EXTENSION)
    del test_item["properties"]["proj:epsg"]

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_sar_extension_validation_error():
    test_item = request(SAR_EXTENSION)
    test_item["properties"]["sar:polarizations"] = ["foo", "bar"]

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_sci_extension_validation_error():
    test_item = request(SCIENTIFIC_EXTENSION)
    test_item["properties"]["sci:doi"] = [43]

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_single_file_stac_validation_error():
    test_item = request(SINGLE_FILE_STAC)
    del test_item["collections"]

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_version_extension_validation_error():
    test_item = request(VERSION_EXTENSION_ITEM)

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_view_extension_validation_error():
    test_item = request(VIEW_EXTENSION)
    test_item["properties"]["view:off_nadir"] = "foo"

    with pytest.raises(ValidationError):
        item = Item(**test_item)


def test_invalid_geometry():
    test_item = request(EO_EXTENSION)

    # Remove the last coordinate
    test_item["geometry"]["coordinates"][0].pop(-1)

    with pytest.raises(ValidationError) as e:
        Item(**test_item)

    assert "Each linear ring must end where it started" in str(e.value)


def test_asset_extras():
    test_item = request(EO_EXTENSION)
    for asset in test_item['assets']:
        test_item['assets'][asset]['foo'] = 'bar'

    item = Item(**test_item)
    for (asset_name, asset) in item.assets.items():
        assert asset.foo == 'bar'


def test_geo_interface():
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    geom = shape(item.geometry)
    test_item["geometry"] = geom
    item = Item(**test_item)


def test_api_conformance():
    ConformanceClasses(conformsTo=[
        "https://conformance-class-1",
        "http://conformance-class-2"
    ])


def test_api_conformance_invalid_url():
    with pytest.raises(ValidationError):
        ConformanceClasses(conformsTo=[
            "s3://conformance-class"
        ])


def test_api_landing_page():
    LandingPage(
        description="stac-api landing page",
        stac_extensions=["eo", "proj"],
        links=[
            Link(
                href="http://link",
                rel="self",
            )
        ]
    )


def test_search():
    Search(
        collections=["collection1", "collection2"]
    )


def test_search_by_id():
    Search(
        collections=["collection1", "collection2"],
        ids=["id1", "id2"]
    )


def test_spatial_search():
    # Search with bbox
    Search(
        collections=["collection1", "collection2"],
        bbox=[-180, -90, 180, 90]
    )

    # Search with geojson
    Search(
        collections=["collection1", "collection2"],
        intersects={"type": "Point", "coordinates": [0,0]}
    )


def test_invalid_spatial_search():
    # bbox and intersects are mutually exclusive
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            intersects={"type": "Point", "coordinates": [0, 0]},
            bbox=[-180, -90, 180, 90]
        )

    # Invalid geojson
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            intersects={"type": "Polygon", "coordinates": [0]}
        )


def test_temporal_search():
    # Test single tailed
    utcnow = datetime.utcnow().strftime(DATETIME_RFC339)
    search = Search(
        collections=["collection1"],
        datetime=utcnow
    )
    assert len(search.datetime) == 2
    assert search.datetime == ["..", utcnow]

    # Test two tailed
    search = Search(
        collections=["collection1"],
        datetime=f"{utcnow}/{utcnow}"
    )
    assert len(search.datetime) == 2
    assert search.datetime == [utcnow, utcnow]

    search = Search(
        collections=["collection1"],
        datetime=f"{utcnow}/.."
    )
    assert len(search.datetime) == 2
    assert search.datetime == [utcnow, ".."]

    # Test open date range
    search = Search(
        collections=["collection1"],
        datetime=f"../.."
    )
    assert len(search.datetime) == 2
    assert search.datetime == ["..", ".."]


def test_invalid_temporal_search():
    # Not RFC339
    utcnow = datetime.utcnow().strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        search = Search(
            collections=["collection1"],
            datetime=utcnow
        )

    # End date is before start date
    start = datetime.utcnow()
    time.sleep(2)
    end = datetime.utcnow()
    with pytest.raises(ValidationError):
        search = Search(
            collections=["collection1"],
            datetime=f"{end.strftime(DATETIME_RFC339)}/{start.strftime(DATETIME_RFC339)}"
        )


def test_api_context_extension():
    item_collection = request(ITEM_COLLECTION)
    item_collection.update({
        'context': {
            'returned': 10,
            'limit': 10,
            'matched': 100
        }
    })
    ItemCollection(**item_collection)


def test_api_context_extension_invalid():
    item_collection = request(ITEM_COLLECTION)
    item_collection.update({
        'context': {
            'returned': 20,
            'limit': 10,
            'matched': 100
        }
    })

    with pytest.raises(ValidationError):
        ItemCollection(**item_collection)


def test_api_fields_extension():
    search = Search(
        collections=["collection1"],
        fields={
            "includes": {"field1", "field2"},
            "excludes": {"field3", "field4"}
        }
    )


def test_api_paging_extension():
    item_collection = request(ITEM_COLLECTION)
    item_collection['links'] += [
        {
            'rel': 'next',
            'method': 'GET',
            'href': 'http://next'
        },
        {
            'rel': 'previous',
            'method': 'GET',
            'href': 'http://prev'
        }
    ]
    ItemCollection(**item_collection)


def test_api_invalid_paging_link():
    # Invalid rel type
    with pytest.raises(ValidationError):
        PaginationLink(
            rel="self",
            method="GET",
            href="http://next"
        )

    # Invalid method
    with pytest.raises(ValidationError):
        PaginationLink(
            rel="next",
            method="DELETE",
            href="http://next"
        )


def test_api_query_extension():
    # One field
    Search(
        collections=["collection1", "collection2"],
        query={
            'field': {
                'lt': 100
            }
        }
    )

    # Many fields
    Search(
        collections=["collection1", "collection2"],
        query={
            'field': {
                'lt': 100
            },
            'field1': {
                'gt': 200
            }
        }
    )


def test_api_query_extension_invalid():
    # Invalid operator
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            query={
                'field': {
                    'greater_than': 100
                }
            }
        )


def test_api_sort_extension():
    Search(
        collections=["collection1", "collection2"],
        sortby=[
            {
                "field": "field1",
                "direction": "asc"
            },
            {
                "field": "field2",
                "direction": "desc"
            }
        ]
    )


def test_api_sort_extension_invalid():
    # Invalid sort direction
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1", "collection2"],
            sortby=[
                {
                    "field": "field1",
                    "direction": "ascending"
                }
            ]
        )