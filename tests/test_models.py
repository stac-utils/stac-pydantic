import json
from typing import Literal

import pytest
from pydantic import ConfigDict, ValidationError
from shapely.geometry import shape

from stac_pydantic import Collection, Item, ItemProperties
from stac_pydantic.extensions import _fetch_and_cache_schema, validate_extensions
from stac_pydantic.links import Link, Links
from stac_pydantic.shared import MimeTypes, StacCommonMetadata

from .conftest import dict_match, request

COLLECTION = "landsat-collection.json"
ITEM_COLLECTION = "itemcollection-sample-full.json"
SINGLE_FILE_STAC = "example-search.json"

# ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}/extensions
# /asset/examples/example-landsat8.json"
# COLLECTION_ASSET_EXTENSION = f"https://raw.githubusercontent.com/radiantearth/stac-spec/v{STAC_VERSION}
# /extensions/collection-assets/examples/example-esm.json"
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

ITEM_GEOMETRY_NULL = "example-item_geometry-null.json"


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
    valid_item = Item(**test_item).model_dump()
    dict_match(test_item, valid_item)


def test_sar_extensions() -> None:
    test_item = request(SAR_EXTENSION)
    valid_item = Item(**test_item).model_dump()
    dict_match(test_item, valid_item)


def test_proj_extension() -> None:
    # The example item uses an invalid band name
    test_item = request(PROJ_EXTENSION)
    test_item["stac_extensions"][1] = (
        "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json"
    )
    test_item["assets"]["B8"]["eo:bands"][0]["common_name"] = "pan"

    valid_item = Item.model_validate(test_item).model_dump()
    dict_match(test_item, valid_item)


def test_version_extension_item() -> None:
    test_item = request(VERSION_EXTENSION_ITEM)
    valid_item = Item(**test_item).model_dump()
    dict_match(test_item, valid_item)


def test_version_extension_collection() -> None:
    test_coll = request(VERSION_EXTENSION_COLLECTION)
    valid_coll = Collection(**test_coll).model_dump()
    dict_match(test_coll, valid_coll)


def test_item_assets_extension() -> None:
    test_coll = request(ITEM_ASSET_EXTENSION)
    valid_coll = Collection(**test_coll).model_dump()
    dict_match(test_coll, valid_coll)


def test_label_extension() -> None:
    test_item = request(LABEL_EXTENSION)

    # This example contains an invalid geometry (linear ring does not close)
    coords = test_item["geometry"]["coordinates"]
    assert len(coords[0]) == 4
    coords[0].append(coords[0][0])
    test_item["geometry"]["coordinates"] = coords

    valid_item = Item(**test_item).model_dump()
    dict_match(test_item, valid_item)


def test_explicit_extension_validation() -> None:
    test_item = request(EO_EXTENSION)

    # This item implements the eo and view extensions
    assert test_item["stac_extensions"][:-1] == [
        "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
        "https://stac-extensions.github.io/view/v1.0.0/schema.json",
    ]

    validate_extensions(test_item)


def test_extension_validation_schema_cache() -> None:
    # Defines 3 extensions, but one is a non-existing URL
    test_item = request(EO_EXTENSION)

    _fetch_and_cache_schema.cache_clear()

    assert not validate_extensions(test_item)
    assert _fetch_and_cache_schema.cache_info().hits == 0
    assert _fetch_and_cache_schema.cache_info().misses == 3

    assert not validate_extensions(test_item)
    assert _fetch_and_cache_schema.cache_info().hits == 2
    # The non-existing URL will have failed, hence retried
    assert _fetch_and_cache_schema.cache_info().misses == 4


@pytest.mark.parametrize(
    "infile,model",
    [(EO_EXTENSION, Item), (COLLECTION, Collection)],
)
def test_to_json(infile, model):
    test_item = request(infile)
    validated = model(**test_item)
    dict_match(json.loads(validated.model_dump_json()), validated.model_dump())


def test_item_to_json() -> None:
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    dict_match(json.loads(item.model_dump_json()), item.model_dump())


def test_invalid_geometry() -> None:
    test_item = request(EO_EXTENSION)

    # Remove the last coordinate
    test_item["geometry"]["coordinates"][0].pop(-1)

    with pytest.raises(ValidationError):
        Item(**test_item)


def test_asset_extras() -> None:
    test_item = request(EO_EXTENSION)
    for asset in test_item["assets"]:
        test_item["assets"][asset]["foo"] = "bar"

    item = Item(**test_item)
    for _, asset in item.assets.items():
        assert asset.foo == "bar"


def test_geo_interface() -> None:
    test_item = request(EO_EXTENSION)
    item = Item(**test_item)
    geom = shape(item.geometry)
    test_item["geometry"] = geom
    Item(**test_item)


@pytest.mark.parametrize(
    "args",
    [
        {"datetime": "2024-01-01T00:00:00Z"},
        {
            "datetime": None,
            "start_datetime": "2024-01-01T00:00:00Z",
            "end_datetime": "2024-01-02T00:00:00Z",
        },
        {
            "datetime": "2024-01-01T00:00:00Z",
            "start_datetime": "2024-01-01T00:00:00Z",
            "end_datetime": "2024-01-02T00:00:00Z",
        },
    ],
)
def test_stac_common_dates(args) -> None:
    StacCommonMetadata(**args)


def test_stac_null_datetime_required() -> None:
    with pytest.raises(ValidationError):
        StacCommonMetadata(
            **{
                "start_datetime": "2024-01-01T00:00:00Z",
                "end_datetime": "2024-01-02T00:00:00Z",
            }
        )


@pytest.mark.parametrize(
    "args",
    [
        {"datetime": None},
        {"datetime": None, "start_datetime": "2024-01-01T00:00:00Z"},
        {"datetime": None, "end_datetime": "2024-01-01T00:00:00Z"},
    ],
)
def test_stac_common_no_dates(args) -> None:
    with pytest.raises(
        ValueError,
        match="start_datetime and end_datetime must be specified when datetime is null",
    ):
        StacCommonMetadata(**args)


@pytest.mark.parametrize(
    "args",
    [
        {"datetime": "2024-01-01T00:00:00Z", "start_datetime": "2024-01-01T00:00:00Z"},
        {"datetime": "2024-01-01T00:00:00Z", "end_datetime": "2024-01-01T00:00:00Z"},
    ],
)
def test_stac_common_start_and_end(args) -> None:
    with pytest.raises(
        ValueError,
        match="use of start_datetime or end_datetime requires the use of the other",
    ):
        StacCommonMetadata(**args)


def test_declared_model() -> None:
    class TestProperties(ItemProperties):
        foo: str
        bar: int

        model_config = ConfigDict(
            populate_by_name=True,
            alias_generator=lambda field_name: f"test:{field_name}",
        )

    class TestItem(Item):
        properties: TestProperties

    test_item = request(EO_EXTENSION)
    del test_item["stac_extensions"]
    test_item["properties"] = {
        "datetime": test_item["properties"]["datetime"],
        "test:foo": "mocked",
        "test:bar": 1,
    }

    valid_item = TestItem(**test_item).model_dump()

    assert "test:foo" in valid_item["properties"]
    assert "test:bar" in valid_item["properties"]


def test_item_factory_custom_base() -> None:
    class TestProperties(ItemProperties):
        foo: Literal["bar"] = "bar"

    class TestItem(Item):
        properties: TestProperties

    test_item = request(EO_EXTENSION)

    model = TestItem(**test_item)
    assert model.properties.foo == "bar"


def test_serialize_namespace() -> None:
    test_item = request(SAR_EXTENSION)
    valid_item = Item(**test_item)
    assert "sar:instrument_mode" in valid_item.model_dump()["properties"]


def test_excludes() -> None:
    test_item = request(EO_EXTENSION)
    valid_item = Item(**test_item).model_dump(
        by_alias=True, exclude_unset=True, exclude={"properties": {"bands"}}
    )
    assert "eo:bands" not in valid_item["properties"]


def test_validate_extensions() -> None:
    test_item = request(SAR_EXTENSION)
    assert validate_extensions(test_item)


def test_validate_extensions_reraise_exception() -> None:
    test_item = request(EO_EXTENSION)
    del test_item["properties"]["datetime"]

    with pytest.raises(ValidationError):
        Item.model_validate(test_item)
        validate_extensions(test_item, reraise_exception=True)


def test_validate_extensions_rfc3339_with_partial_seconds() -> None:
    test_item = request(SAR_EXTENSION)
    test_item["properties"]["updated"] = "2018-10-01T01:08:32.033Z"
    assert validate_extensions(test_item)


@pytest.mark.parametrize("url,cls", [[EO_EXTENSION, Item], [COLLECTION, Collection]])
def test_extension(url, cls):
    test_data = request(url)
    test_data["stac_extensions"].append("https://foo")
    model = cls.model_validate(test_data)
    assert "https://foo/" in list(map(str, model.stac_extensions))


def test_resolve_link() -> None:
    link = Link(href="/hello/world", type=MimeTypes.jpeg, rel="test")
    link.resolve(base_url="http://base_url.com")
    assert link.href == "http://base_url.com/hello/world"


def test_resolve_links() -> None:
    links = Links.model_validate(
        [Link(href="/hello/world", type=MimeTypes.jpeg, rel="test")]
    )
    links.resolve(base_url="http://base_url.com")
    for link in links.link_iterator():
        assert link.href == "http://base_url.com/hello/world"


def test_geometry_null_item() -> None:
    test_item = request(ITEM_GEOMETRY_NULL)
    valid_item = Item(**test_item).model_dump()
    dict_match(test_item, valid_item)


def test_item_bbox_validation() -> None:
    test_item = request(LABEL_EXTENSION)
    test_item["bbox"] = None
    with pytest.raises(ValueError, match="bbox is required if geometry is not null"):
        Item(**test_item)
