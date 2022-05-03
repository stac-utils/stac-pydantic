from datetime import datetime

import pytest
from pydantic import ValidationError
from shapely.geometry import Polygon, shape  # type: ignore

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


@pytest.mark.parametrize(
    "bbox",
    [
        (100.0, 1.0, 105.0, 0.0),  # ymin greater than ymax
        (100.0, 0.0, 95.0, 1.0),  # xmin greater than xmax
        (100.0, 0.0, 5.0, 105.0, 1.0, 4.0),  # min elev greater than max elev
        (-200.0, 0.0, 105.0, 1.0),  # xmin is invalid WGS84
        (100.0, -100, 105.0, 1.0),  # ymin is invalid WGS84
        (100.0, 0.0, 190.0, 1.0),  # xmax is invalid WGS84
        (100.0, 0.0, 190.0, 100.0),  # ymax is invalid WGS84
        (-200.0, 0.0, 0.0, 105.0, 1.0, 4.0),  # xmin is invalid WGS84 (3d)
        (100.0, -100, 0.0, 105.0, 1.0, 4.0),  # ymin is invalid WGS84 (3d)
        (100.0, 0.0, 0.0, 190.0, 1.0, 4.0),  # xmax is invalid WGS84 (3d)
        (100.0, 0.0, 0.0, 190.0, 100.0, 4.0),  # ymax is invalid WGS84 (3d)
    ],
)
def test_search_invalid_bbox(bbox):
    with pytest.raises(ValidationError):
        Search(collections=["foo"], bbox=bbox)
