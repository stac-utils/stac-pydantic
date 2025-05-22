from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from shapely.geometry import Polygon, shape

from stac_pydantic.api.search import Search


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
    utcnow = datetime.now(timezone.utc)
    utcnow_str = utcnow.isoformat()
    search = Search(collections=["collection1"], datetime=utcnow_str)
    assert search.start_date == utcnow
    assert search.end_date == utcnow


def test_datetime_clean():
    # ref: https://github.com/stac-utils/stac-pydantic/issues/170
    utcnow = datetime.now(timezone.utc)
    utcnow_str = utcnow.isoformat()
    search = Search(datetime=utcnow_str)
    assert search.start_date == utcnow
    assert search.end_date == utcnow

    search = Search()
    assert not search.start_date
    assert not search.end_date


def test_temporal_search_two_tailed():
    # Test two tailed
    utcnow = datetime.now(timezone.utc)
    utcnow_str = utcnow.isoformat()
    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/{utcnow_str}")
    assert search.start_date == search.end_date == utcnow

    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/..")
    assert search.start_date == utcnow
    assert search.end_date is None

    search = Search(collections=["collection1"], datetime=f"{utcnow_str}/")
    assert search.start_date == utcnow
    assert search.end_date is None

    search = Search(collections=["collection1"], datetime=f"../{utcnow_str}")
    assert search.start_date is None
    assert search.end_date == utcnow

    search = Search(collections=["collection1"], datetime=f"/{utcnow_str}")
    assert search.start_date is None
    assert search.end_date == utcnow


def test_temporal_search_open():
    # Test open date range
    search = Search(collections=["collection1"], datetime="../..")
    assert search.start_date is None
    assert search.end_date is None


def test_invalid_temporal_search_date():
    # Just a date, no time
    utcnow = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        Search(collections=["collection1"], datetime=utcnow)


def test_invalid_temporal_search_too_many():
    # Too many dates
    t1 = datetime.now(timezone.utc)
    t2 = t1 + timedelta(seconds=100)
    t3 = t2 + timedelta(seconds=100)
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1"],
            datetime=f"{t1.isoformat()}/{t2.isoformat()}/{t3.isoformat()}",
        )


def test_invalid_temporal_search_date_wrong_order():
    # End date is before start date
    start = datetime.now(timezone.utc)
    end = start - timedelta(seconds=100)
    with pytest.raises(ValidationError):
        Search(
            collections=["collection1"],
            datetime=f"{start.isoformat()}/{end.isoformat()}",
        )


def test_search_geometry_bbox():
    search = Search(collections=["foo", "bar"], bbox=[0, 0, 1, 1])
    geom1 = shape(search.spatial_filter)
    geom2 = Polygon.from_bounds(*search.bbox)
    assert (geom1.intersection(geom2).area / geom1.union(geom2).area) == 1.0


@pytest.mark.parametrize(
    "bbox",
    [
        (100.0, 1.0),  # 1D Coordinates
        (100.0, 1.0, 105.0, 0.0),  # ymin greater than ymax
        (100.0, 0.0, 5.0, 105.0, 1.0, 4.0),  # min elev greater than max elev
        (-200.0, 0.0, 105.0, 1.0),  # xmin is invalid WGS84
        (
            105.0,
            0.0,
            100.0,
            1.0,
        ),  # xmin greater than xmax but not crossing Antimeridian
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


def test_search_none_datetime() -> None:
    Search(datetime=None)


@pytest.mark.parametrize(
    "dt,start,end",
    [
        # unique datetime, start/end == datetime
        ["1985-04-12T23:20:50.52Z", False, False],
        # start datetime is None
        ["../1985-04-12T23:20:50.52Z", True, False],
        ["/1985-04-12T23:20:50.52Z", True, False],
        # end datetime is None
        ["1985-04-12T23:20:50.52Z/..", False, True],
        ["1985-04-12T23:20:50.52Z/", False, True],
        # Both start/end datetime are available
        ["1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z", False, False],
        ["1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00", False, False],
        ["1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00", False, False],
    ],
)
def test_search_datetime(dt, start, end):
    s = Search(datetime=dt)
    assert s.datetime is not None
    assert (s.start_date is None) == start
    assert (s.end_date is None) == end


@pytest.mark.parametrize(
    "dt",
    [
        "/"
        "../"
        "/.."
        "../.."
        "/1984-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z",  # extra start /
        "1984-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z/",  # extra end /
        "1986-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z",  # start > end
    ],
)
def test_search_invalid_datetime(dt):
    with pytest.raises(ValidationError):
        Search(datetime=dt)
