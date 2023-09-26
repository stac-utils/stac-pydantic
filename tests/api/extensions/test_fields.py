from datetime import datetime

from shapely.geometry import Polygon

from stac_pydantic.api import Item
from stac_pydantic.api.extensions.fields import FieldsExtension
from stac_pydantic.api.search import Search


def test_fields_filter_item():
    fields = FieldsExtension(
        includes={"id", "geometry", "properties.foo"}, excludes={"properties.bar"}
    )

    item = Item(
        id="test-fields-filter",
        geometry=Polygon.from_bounds(0, 0, 0, 0),
        properties={"datetime": datetime.utcnow(), "foo": "foo", "bar": "bar"},
        assets={},
        links=[
            {"href": "http://link", "rel": "self"},
            {
                "href": "http://root",
                "rel": "root",
            },
            {
                "href": "http://collection",
                "rel": "collection",
            },
        ],
        bbox=[0, 0, 0, 0],
        type="Feature",
    )
    print(fields.filter)
    d = item.model_dump(**fields.filter)
    assert d.pop("id") == item.id
    assert d.pop("geometry") == item.geometry.model_dump(exclude_unset=True)
    props = d.pop("properties")
    assert props["foo"] == "foo"

    assert not props.get("bar")
    assert not d


def test_api_fields_extension():
    Search(
        collections=["collection1"],
        fields={"includes": {"field1", "field2"}, "excludes": {"field3", "field4"}},
    )
