import json
import os
from copy import deepcopy
from typing import List, Optional, Type

import dictdiffer
import pytest
import requests
from click.testing import CliRunner
from pydantic import BaseModel, TypeAdapter

from stac_pydantic.shared import UtcDatetime


def request(url: str, path: Optional[List[str]] = None):
    if path is None:
        path = ["tests", "example_stac"]

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


# Use a TypeAdapter to parse any datetime strings in a consistent manner
UtcDatetimeAdapter = TypeAdapter(UtcDatetime)


def dict_match(d1: dict, d2: dict):
    test = dictdiffer.diff(d1, d2)
    for diff in test:
        # geojson-pydantic uses tuples for coordinates, but sometimes the example data are lists
        if "coordinates" in diff[1]:
            assert list(diff[2][0]) == list(diff[2][1])
        # same for bbox
        elif "bbox" in diff[1]:
            assert list(diff[2][0]) == list(diff[2][1])
        # RFC3339 is quite flexible and the test data uses various options to represent datetimes.
        # The datetime string stac-pydantic outputs may not be identical to the input. So we need
        # to compare the values as datetime objects.
        elif "datetime" in diff[1]:
            dates = [
                UtcDatetimeAdapter.validate_strings(date)
                if isinstance(date, str)
                else date
                for date in diff[2]
            ]
            assert dates[0] == dates[1]
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
    path: Optional[List[str]] = None,
) -> None:
    if path is None:
        path = ["tests", "example_stac"]

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
