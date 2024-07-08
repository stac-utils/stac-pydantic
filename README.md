# stac-pydantic

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/stac-utils/stac-pydantic/cicd.yml?style=for-the-badge)](https://github.com/stac-utils/stac-pydantic/actions/workflows/cicd.yml)

[Pydantic](https://pydantic-docs.helpmanual.io/) models for [STAC](https://github.com/radiantearth/stac-spec) Catalogs, Collections, Items, and the [STAC API](https://github.com/radiantearth/stac-api-spec) spec.
Initially developed by [arturo-ai](https://github.com/arturo-ai).

The main purpose of this library is to provide reusable request/response models for tools such as [fastapi](https://fastapi.tiangolo.com/).
For more comprehensive schema validation and robust extension support, use [pystac](https://github.com/stac-utils/pystac).

## Installation

```shell
python -m pip install stac-pydantic

# or

python -m pip install stac-pydantic["validation"]
```

For local development:

```shell
python -m pip install -e '.[dev,lint]'
```

| stac-pydantic | STAC Version | STAC API Version | Pydantic Version |
|--------------|---------------|------------------|-----------------|
| 1.2.x         | 1.0.0-beta.1 | <1* | ^1.6 |
| 1.3.x         | 1.0.0-beta.2 | <1* | ^1.6 |
| 2.0.x         | 1.0.0        | <1* | ^1.6 |
| 3.0.x         | 1.0.0        | 1.0.0 | ^2.4 |
| 3.1.x         | 1.0.0        | 1.0.0 | ^2.4 |

\* various beta releases, specs not fully implemented

## Development

Install the [pre-commit](https://pre-commit.com/) hooks:

```shell
pre-commit install
```

## Testing

Ensure you have all Python versions installed that the tests will be run against. If using pyenv, run:

```shell
pyenv install 3.8.18
pyenv install 3.9.18
pyenv install 3.10.13
pyenv install 3.11.5
pyenv local 3.8.18 3.9.18 3.10.13 3.11.5
```

Run the entire test suite:

```shell
tox
```

Run a single test case using the standard pytest convention:

```shell
python -m pytest -v tests/test_models.py::test_item_extensions
```

## Usage

### Loading Models

Load data into models with standard pydantic:

```python
from stac_pydantic import Catalog

stac_catalog = {
  "type": "Catalog",
  "stac_version": "1.0.0",
  "id": "sample",
  "description": "This is a very basic sample catalog.",
  "links": [
    {
      "href": "item.json",
      "rel": "item"
    }
  ]
}

catalog = Catalog(**stac_catalog)
assert catalog.id == "sample"
assert catalog.links[0].href == "item.json"
```

### Extensions

STAC defines many extensions which let the user customize the data in their catalog. `stac-pydantic.extensions.validate_extensions` gets the JSON schemas from the URLs provided in the `stac_extensions` property (caching the last fetched ones), and will validate a `dict`, `Item`, `Collection` or `Catalog` against those fetched schemas:

```python
from stac_pydantic import Item
from stac_pydantic.extensions import validate_extensions

stac_item = {
    "id": "12345",
    "type": "Feature",
    "stac_extensions": [
        "https://stac-extensions.github.io/eo/v1.0.0/schema.json"
    ],
    "geometry": { "type": "Point", "coordinates": [0, 0] },
    "bbox": [0.0, 0.0, 0.0, 0.0],
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
        "eo:cloud_cover": 25,
    },
    "links": [],
    "assets": {},
}

model = Item(**stac_item)
validate_extensions(model, reraise_exception=True)
assert getattr(model.properties, "eo:cloud_cover") == 25
```

The complete list of current STAC Extensions can be found [here](https://stac-extensions.github.io/).

#### Vendor Extensions

The same procedure described above works for any STAC Extension schema as long as it can be loaded from a public url.

### STAC API

The [STAC API Specs](https://github.com/radiantearth/stac-api-spec) extent the core STAC specification for implementing dynamic catalogs. STAC Objects used in an API context should always import models from the `api` subpackage. This package extends
Catalog, Collection, and Item models with additional fields and validation rules and introduces Collections and ItemCollections models and Pagination/ Search Links.
It also implements models for defining ItemSeach queries.

```python
from stac_pydantic.api import Item, ItemCollection

stac_item = Item(**{
    "id": "12345",
    "type": "Feature",
    "stac_extensions": [],
    "geometry": { "type": "Point", "coordinates": [0, 0] },
    "bbox": [0.0, 0.0, 0.0, 0.0],
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
    },
    "collection": "CS3",
    "links": [
          {
            "rel": "self",
            "href": "http://stac.example.com/catalog/collections/CS3-20160503_132130_04/items/CS3-20160503_132130_04.json"
          },
          {
            "rel": "collection",
            "href": "http://stac.example.com/catalog/CS3-20160503_132130_04/catalog.json"
          },
          {
            "rel": "root",
            "href": "http://stac.example.com/catalog"
          }],
    "assets": {},
    })

stac_item_collection = ItemCollection(**{
    "type": "FeatureCollection",
    "features": [stac_item],
    "links": [
          {
            "rel": "self",
            "href": "http://stac.example.com/catalog/search?collection=CS3",
            "type": "application/geo+json"
          },
          {
            "rel": "root",
            "href": "http://stac.example.com/catalog",
            "type": "application/json"
          }],
    })
```

### Exporting Models

Most STAC extensions are namespaced with a colon (ex `eo:gsd`) to keep them distinct from other extensions.  Because
Python doesn't support the use of colons in variable names, we use [Pydantic aliasing](https://pydantic-docs.helpmanual.io/usage/model_config/#alias-generator)
to add the namespace upon model export.  This requires [exporting](https://pydantic-docs.helpmanual.io/usage/exporting_models/)
the model with the `by_alias = True` parameter. Export methods (`model_dump()` and `model_dump_json()`) for models in this library have `by_alias` and `exclude_unset` st to `True` by default:

```python
item_dict = item.model_dump()
assert item_dict['properties']['landsat:row'] == item.properties.row == 250
```

### CLI

```text
Usage: stac-pydantic [OPTIONS] COMMAND [ARGS]...

  stac-pydantic cli group

Options:
  --help  Show this message and exit.

Commands:
  validate-item  Validate STAC Item
```
