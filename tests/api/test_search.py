import time
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from shapely.geometry import Polygon, shape

from stac_pydantic.api.search import Search
from stac_pydantic.shared import DATETIME_RFC339


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
            "geometries": [{"type": "Point", "coordinates": [0, 0]}],
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
    assert search.start_date is None
    assert search.end_date == utcnow


def test_temporal_search_two_tailed():
    # Test two tailed
    utcnow = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
    utcnow_str = utcnow.strftime(DATETIME_RFC339)
    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/{utcnow_str}")
    assert search.start_date == search.end_date == utcnow

    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/..")
    assert search.start_date == utcnow
    assert search.end_date is None

    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/")
    assert search.start_date == utcnow
    assert search.end_date is None


def test_temporal_search_open():
    # Test open date range
    search = Search(collections=["collection1"], datetime="../..")
    assert search.start_date is None
    assert search.end_date is None


def test_invalid_temporal_search():
    # Not RFC339
    utcnow = datetime.utcnow().strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        Search(collections=["collection1"], datetime=utcnow)

    t1 = datetime.utcnow()
    t2 = t1 + timedelta(seconds=100)
    t3 = t2 + timedelta(seconds=100)
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1"],
            datetime=f"{t1.strftime(DATETIME_RFC339)}/{t2.strftime(DATETIME_RFC339)}/{t3.strftime(DATETIME_RFC339)}",
        )

    # End date is before start date
    start = datetime.utcnow()
    time.sleep(2)
    end = datetime.utcnow()
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1"],
            datetime=f"{end.strftime(DATETIME_RFC339)}/{start.strftime(DATETIME_RFC339)}",
        )


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
