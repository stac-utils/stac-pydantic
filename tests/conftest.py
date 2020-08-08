import json

import pytest
import requests
from click.testing import CliRunner


def request(url: str):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def dict_match(d1: dict, d2: dict):
    d1 = json.dumps(
        json.loads(json.dumps(d1, sort_keys=True), parse_int=lambda x: float(x)),
        sort_keys=True,
    )
    d2 = json.dumps(
        json.loads(json.dumps(d2, sort_keys=True), parse_int=lambda x: float(x)),
        sort_keys=True,
    )
    assert d1 == d2


@pytest.fixture
def cli_runner():
    return CliRunner()
