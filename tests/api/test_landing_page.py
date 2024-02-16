import jsonschema
import pytest
import requests
import yaml
from pydantic import ValidationError

from stac_pydantic import Catalog
from stac_pydantic.api.landing import LandingPage
from stac_pydantic.api.links import Link
from stac_pydantic.api.version import STAC_API_VERSION

from ..conftest import compare_example, request

valid_examples = ["landing_page_core.json", "landing_page_ogcapi-features.json"]
schema_url = [
    f"https://raw.githubusercontent.com/radiantearth/stac-api-spec/v{STAC_API_VERSION}/core/commons.yaml",
    f"https://raw.githubusercontent.com/radiantearth/stac-api-spec/v{STAC_API_VERSION}/ogcapi-features/openapi-features.yaml",
]

unique_combinations = []

for i in range(len(valid_examples)):
    for j in range(len(schema_url)):
        unique_combinations.append((valid_examples[i], schema_url[j]))


@pytest.mark.parametrize("example_url", valid_examples)
def test_landing_page(example_url):
    compare_example(
        example_url,
        LandingPage,
        path=["tests", "api", "examples", f"v{STAC_API_VERSION}"],
    )


@pytest.mark.parametrize("example_url", valid_examples)
def test_landing_page_invalid_core(example_url):
    example = request(
        example_url, path=["tests", "api", "examples", f"v{STAC_API_VERSION}"]
    )
    example["links"] = []
    with pytest.raises(ValidationError):
        LandingPage(**example)


@pytest.mark.parametrize("example_url", valid_examples)
def test_landing_page_invalid_features(example_url):
    example = request(
        example_url, path=["tests", "api", "examples", f"v{STAC_API_VERSION}"]
    )
    links = [
        link for link in example["links"] if link["rel"] not in ["data", "conformance"]
    ]
    example["links"] = links

    with pytest.raises(ValidationError):
        LandingPage(**example)


@pytest.mark.parametrize("example_url,schema_url", unique_combinations)
def test_schema(example_url, schema_url):
    rsp_yaml = requests.get(schema_url).text
    schema = yaml.safe_load(rsp_yaml)

    example = request(
        example_url, path=["tests", "api", "examples", f"v{STAC_API_VERSION}"]
    )
    landing_page = LandingPage(**example).model_dump_json()
    jsonschema.validate(instance=landing_page, schema=schema)


def test_api_landing_page():
    LandingPage(
        type="Catalog",
        id="test-landing-page",
        description="stac-api landing page",
        stac_extensions=[
            "https://raw.githubusercontent.com/stac-extensions/eo/v1.0.0/json-schema/schema.json",
            "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json",
        ],
        conformsTo=[
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ],
        links=[
            Link(
                href="http://link",
                rel="self",
            ),
            Link(
                href="http://root",
                rel="root",
            ),
            Link(
                href="http://service_desc",
                rel="service-desc",
            ),
        ],
    )


def test_api_landing_page_is_catalog():
    landing_page = LandingPage(
        type="Catalog",
        id="test-landing-page",
        description="stac-api landing page",
        stac_extensions=[
            "https://raw.githubusercontent.com/stac-extensions/eo/v1.0.0/json-schema/schema.json",
            "https://raw.githubusercontent.com/stac-extensions/projection/v1.0.0/json-schema/schema.json",
        ],
        conformsTo=[
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ],
        links=[
            Link(
                href="http://link",
                rel="self",
            ),
            Link(
                href="http://root",
                rel="root",
            ),
            Link(
                href="http://service_desc",
                rel="service-desc",
            ),
        ],
    )
    d = landing_page.model_dump()
    Catalog(**d)
