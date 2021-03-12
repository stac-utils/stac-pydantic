from datetime import datetime

from shapely.geometry import Polygon, shape

from stac_pydantic import Item
from stac_pydantic.api.extensions.fields import FieldsExtension
from stac_pydantic.api.search import Search


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


def test_search_geometry_bbox():
    search = Search(collections=["foo", "bar"], bbox=[0, 0, 1, 1])
    geom1 = shape(search.spatial_filter)
    geom2 = Polygon.from_bounds(*search.bbox)
    assert (geom1.intersection(geom2).area / geom1.union(geom2).area) == 1.0
