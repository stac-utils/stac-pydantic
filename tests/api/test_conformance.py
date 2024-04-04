import pytest
from pydantic import ValidationError

from stac_pydantic.api.conformance import Conformance


def test_api_conformance():
    Conformance(
        conformsTo=["https://conformance-class-1", "http://conformance-class-2"]
    )


def test_api_conformance_invalid_url():
    with pytest.raises(ValidationError):
        Conformance(conformsTo=["s3://conformance-class"])
