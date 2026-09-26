"""STAC 1.1 model coverage against the published core schemas."""

import pytest
import requests
from jsonschema import Draft7Validator
from pydantic import ValidationError
from referencing import Registry, Resource

from stac_pydantic import Catalog, Collection, Item
from stac_pydantic.version import STAC_VERSION


def stac_11_objects():
    item = Item(
        id="stac-11-item",
        stac_version="1.1.0",
        type="Feature",
        geometry={"type": "Point", "coordinates": [1, 2]},
        bbox=[1, 2, 1, 2],
        properties={
            "datetime": "2024-01-01T00:00:00Z",
            "keywords": ["example"],
        },
        assets={
            "data": {
                "href": "https://example.com/data.tif",
                "roles": ["data"],
                "bands": [
                    {"name": "red", "data_type": "uint16", "unit": "reflectance"}
                ],
            }
        },
        links=[
            {
                "rel": "self",
                "href": "https://example.com/item.json",
                "method": "GET",
                "headers": {"Accept": ["application/geo+json"]},
                "body": {"example": True},
            }
        ],
    )
    collection = Collection(
        id="stac-11-collection",
        stac_version="1.1.0",
        type="Collection",
        description="An example collection.",
        license="CC-BY-4.0",
        extent={
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [["2024-01-01T00:00:00Z", None]]},
        },
        item_assets={
            "data": {
                "type": "image/tiff",
                "roles": ["data"],
                "bands": [{"name": "red", "data_type": "uint16"}],
            }
        },
        links=[{"rel": "self", "href": "https://example.com/collection.json"}],
    )
    catalog = Catalog(
        id="stac-11-catalog",
        stac_version="1.1.0",
        type="Catalog",
        description="An example catalog.",
        keywords=["example"],
        links=[{"rel": "self", "href": "https://example.com/catalog.json"}],
    )
    return item, collection, catalog


def test_stac_11_fields_are_typed_and_serialized():
    item, collection, catalog = stac_11_objects()

    assert STAC_VERSION == "1.1.0"
    assert item.assets["data"].bands[0].data_type == "uint16"
    assert item.links[0].headers == {"Accept": ["application/geo+json"]}
    assert collection.item_assets["data"].bands[0].name == "red"
    assert "href" not in collection.model_dump()["item_assets"]["data"]
    assert catalog.keywords == ["example"]
    assert all(obj.stac_version == "1.1.0" for obj in (item, collection, catalog))

    with pytest.raises(ValidationError):
        Item.model_validate(
            {
                **item.model_dump(mode="json"),
                "properties": {
                    "datetime": "2024-01-01T00:00:00Z",
                    "data_type": "not-a-type",
                },
            }
        )
    with pytest.raises(ValidationError):
        Collection.model_validate(
            {
                **collection.model_dump(mode="json"),
                "item_assets": {"data": {"href": "https://example.com/data.tif"}},
            }
        )


@pytest.mark.network
def test_stac_11_models_match_official_schemas():
    def retrieve(uri):
        response = requests.get(uri, timeout=10)
        response.raise_for_status()
        return Resource.from_contents(response.json())

    registry = Registry(retrieve=retrieve)
    for obj, path in zip(
        stac_11_objects(),
        (
            "item-spec/json-schema/item.json",
            "collection-spec/json-schema/collection.json",
            "catalog-spec/json-schema/catalog.json",
        ),
        strict=True,
    ):
        uri = f"https://schemas.stacspec.org/v1.1.0/{path}"
        schema = retrieve(uri).contents
        Draft7Validator(
            schema, registry=registry, format_checker=Draft7Validator.FORMAT_CHECKER
        ).validate(obj.model_dump(mode="json", exclude_none=True))
