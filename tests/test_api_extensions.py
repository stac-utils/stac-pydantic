from datetime import datetime

import pytest
from shapely.geometry import Polygon

from stac_pydantic import Item
from stac_pydantic.api.extensions.fields import FieldsExtension


def test_fields_filter():
    fields = FieldsExtension(
        includes={"id", "geometry", "properties.foo"}, excludes={"properties.bar"}
    )

    item = Item(
        id="test-fields-filter",
        geometry=Polygon.from_bounds(0, 0, 0, 0),
        properties={"datetime": datetime.utcnow(), "foo": "foo", "bar": "bar"},
        assets={},
        links=[],
        bbox=[0, 0, 0, 0],
    )

    d = item.to_dict(**fields.filter)
    assert d.pop("id") == item.id
    assert d.pop("geometry") == item.geometry
    props = d.pop("properties")
    assert props["foo"] == "foo"

    assert not props.get("bar")
    assert not d
