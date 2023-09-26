import json
import operator
import os
from copy import deepcopy
from typing import List, Optional, Type

import arrow
import dictdiffer
import pytest
import requests
from click.testing import CliRunner
from pydantic import BaseModel


def request(url: str, path: list[str] = ["tests", "example_stac"]):
    if url.startswith("http"):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    else:
        _full_path = deepcopy(path)
        _full_path.append(url)
        full_path = os.path.join(*_full_path)
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
            dates.sort(reverse=True)
            assert operator.sub(*dates).days == 0
        # any other differences are errors
        elif "stac_extensions" in diff[1]:
            url1, url2 = map(str, diff[2])
            assert url1 == url2

        else:
            raise AssertionError("Unexpected difference: ", diff)


def compare_example(
    example_url: str,
    model: Type[BaseModel],
    fields: Optional[List[str]] = None,
    path: list[str] = ["tests", "example_stac"],
) -> None:
    example = request(example_url, path)
    model_dict = json.loads(model(**example).model_dump_json())

    if fields:
        for field in fields:
            assert model_dict.get(field) == example.get(field)
    else:
        dict_match(model_dict, example)


@pytest.fixture
def cli_runner():
    return CliRunner()
