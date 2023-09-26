import pytest
from pydantic import ValidationError

from stac_pydantic.api.conformance import ConformanceClasses


def test_api_conformance():
    ConformanceClasses(
        conformsTo=["https://conformance-class-1", "http://conformance-class-2"]
    )


def test_api_conformance_invalid_url():
    with pytest.raises(ValidationError):
        ConformanceClasses(conformsTo=["s3://conformance-class"])
