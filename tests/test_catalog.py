from stac_pydantic.catalog import Catalog


def test_catalog():
    # Create a valid Catalog instance
    catalog = Catalog(
        type="Catalog",
        id="my-catalog",
        description="My STAC catalog",
    )

    catalog_json = catalog.model_dump(mode="json")

    # Make default all values are set
    assert catalog_json["id"] == "my-catalog"
    assert catalog_json["description"] == "My STAC catalog"
    assert catalog_json["stac_version"] == "1.0.0"
    assert catalog_json["links"] == []
    assert catalog_json["type"] == "Catalog"

    assert "stac_extensions" not in catalog_json
    assert "title" not in catalog_json
