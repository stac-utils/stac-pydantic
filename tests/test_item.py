import pytest
from ciso8601 import parse_rfc3339
from pydantic import ValidationError

from stac_pydantic.item import Item


def test_item():

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "bbox": [125.6, 10.1, 125.6, 10.1],
        "properties": {"datetime": "2022-01-01T00:00:00Z"},
    }
    item = Item(**item_data)

    item_json = item.model_dump(mode="json")

    # make sure that assets and links are set and parsed correctly
    # datetime should be parsed as string and internally handled as datetime
    # Collection and stac_extensions should not be parsed if not set
    assert item_json["id"] == "sample-item"
    assert item_json["stac_version"] == "1.0.0"
    assert item_json["properties"]["datetime"] == "2022-01-01T00:00:00Z"
    assert item.properties.datetime == parse_rfc3339("2022-01-01T00:00:00Z")
    assert item_json["assets"] == {}
    assert item_json["links"] == []

    assert "collection" not in item_json
    assert "stac_extensions" not in item_json


def test_item_datetime_set_null():

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "bbox": [125.6, 10.1, 125.6, 10.1],
        "properties": {
            "start_datetime": "2022-01-01T00:00:00Z",
            "end_datetime": "2022-12-01T00:00:00Z",
        },
    }
    item = Item(**item_data)

    item_json = item.model_dump(mode="json")

    # make sure datetime is parsed as null and start_datetime and end_datetime are parsed as strings
    assert item_json["properties"]["datetime"] is None
    assert item_json["properties"]["start_datetime"] == "2022-01-01T00:00:00Z"
    assert item_json["properties"]["end_datetime"] == "2022-12-01T00:00:00Z"


@pytest.mark.parametrize(
    "datetime", ["2022-01-01T00:00:00", "2022-01-01", "2022-01", "2022"]
)
def test_item_datetime_no_z(datetime):

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "bbox": [125.6, 10.1, 125.6, 10.1],
        "properties": {"datetime": datetime},
    }
    item = Item(**item_data)

    item_json = item.model_dump(mode="json")

    # The model should fix the date and timezone for us
    assert item_json["properties"]["datetime"] == "2022-01-01T00:00:00Z"


def test_item_bbox_missing():

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "properties": {"datetime": "2022-01-01T00:00:00Z"},
    }

    with pytest.raises(ValidationError) as e:
        Item(**item_data)
        assert e.value.errors() == [
            {
                "loc": ("bbox",),
                "msg": "bbox is required if geometry is not null",
                "type": "value_error",
            }
        ]


@pytest.mark.parametrize("property", ["start_datetime", "end_datetime"])
def test_item_start_end_datetime_missing(property):

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "bbox": [125.6, 10.1, 125.6, 10.1],
        "properties": {
            property: "2022-12-01T00:00:00Z",
        },
    }

    with pytest.raises(ValidationError) as e:
        Item(**item_data)
        assert e.value.errors() == [
            {
                "loc": ("properties",),
                "msg": "start_datetime and end_datetime must be specified when datetime is null",
                "type": "value_error",
            }
        ]


def test_item_datetime_missing():

    item_data = {
        "type": "Feature",
        "id": "sample-item",
        "stac_version": "1.0.0",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "bbox": [125.6, 10.1, 125.6, 10.1],
        "properties": {},
    }

    with pytest.raises(ValidationError) as e:
        Item(**item_data)
        assert e.value.errors() == [
            {
                "loc": ("properties",),
                "msg": "start_datetime and end_datetime must be specified when datetime is null",
                "type": "value_error",
            }
        ]
