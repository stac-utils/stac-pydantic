import functools

import pytest
import requests


@pytest.fixture
def request_test_data():
    @functools.lru_cache()
    def request(url: str):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    return request


@pytest.fixture
def test_equivalency():
    def dict_match(d1: dict, d2: dict):
        for (k, v) in d1.items():
            # Don't validate geometry because validation transforms from list to tuple
            if k not in ("geometry", "bbox"):
                assert d2[k] == v

    return dict_match
