import json
import operator
import os

import arrow
import dictdiffer  # type: ignore
import pytest
import requests
from click.testing import CliRunner


def request(url: str):
    if url.startswith("http"):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    else:
        full_path = os.path.join(*["tests", "example_stac", url])
        with open(full_path, "r") as local_file:
            lines = local_file.readlines()
        full_file = "".join(lines)
        return json.loads(full_file)


def dict_match(d1: dict, d2: dict):
    test = dictdiffer.diff(d1, d2)
    for diff in test:
        # geojson-pydantic uses tuples for coordinates, but sometimes the example data are lists
        if "coordinates" in diff[1]:
            assert list(diff[2][0]) == list(diff[2][1])
        # same for bbox
        elif "bbox" in diff[1]:
            assert list(diff[2][0]) == list(diff[2][1])
        # test data is pretty variable with how it represents datetime, RFC3339 is quite flexible
        # but stac-pydantic only supports a single datetime format, so just validate to the day.
        elif "datetime" in diff[1]:
            dates = []
            for date in diff[2]:
                if isinstance(date, str):
                    date = arrow.get(date)
                dates.append(date)
            assert operator.sub(*dates).days == 0
        # any other differences are errors
        else:
            raise AssertionError("Unexpected difference: ", diff)


@pytest.fixture
def cli_runner():
    return CliRunner()
