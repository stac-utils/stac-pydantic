# stac-pydantic ![tests](https://github.com/arturo-ai/stac-pydantic/workflows/cicd/badge.svg)
[Pydantic](https://pydantic-docs.helpmanual.io/) models for [STAC](https://github.com/radiantearth/stac-spec) Catalogs, Collections, Items, and the [STAC API](https://github.com/radiantearth/stac-api-spec) spec.  Initially developed by [arturo-ai](https://github.com/arturo-ai).

## Installation
```
pip install stac-pydantic
```

For local development:
```
pip install -e .["dev"]
```

| stac-pydantic | stac     |
|-------------------|--------------|
| 1.1.x             | 0.9.0        |
| 1.2.x             | 1.0.0-beta.1 |
| 1.3.x             | 1.0.0-beta.2 |
| 2.0.x             | 1.0.0        |

## Testing
Run the entire test suite:
```
tox
```

Run a single test case using the standard pytest convention:
```
pytest -v tests/test_models.py::test_item_extensions
```

## Usage
### Loading Models
Load data into models with standard pydantic:
```python
from stac_pydantic import Catalog

stac_catalog = {
  "stac_version": "0.9.0",
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
STAC defines many extensions which let the user customize the data in their catalog. `stac-pydantic.extensions.validate_extensions` will validate a `dict`, `Item`, `Collection` or `Catalog` against the schema urls provided in the `stac_extensions` property: 

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
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
        "eo:cloud_cover": 25,
    },
    "links": [],
    "assets": [],
}

model = Item(**stac_item) 
validate_extensions(model, reraise_exception=True)
assert getattr(model.properties, "eo:cloud_cover") == 25 
```

The complete list of current STAC Extensions can be found [here](https://stac-extensions.github.io/).

#### Vendor Extensions
The same procedure described above works for any STAC Extension schema as long as it can be loaded from a public url.

### Exporting Models
Most STAC extensions are namespaced with a colon (ex `eo:gsd`) to keep them distinct from other extensions.  Because
Python doesn't support the use of colons in variable names, we use [Pydantic aliasing](https://pydantic-docs.helpmanual.io/usage/model_config/#alias-generator)
to add the namespace upon model export.  This requires [exporting](https://pydantic-docs.helpmanual.io/usage/exporting_models/)
the model with the `by_alias = True` parameter.  A convenience method (``to_dict()``) is provided to export models with
extension namespaces:

```python
item_dict = item.to_dict()
assert item_dict['properties']['landsat:row'] == item.properties.row == 250
```

### CLI
```
Usage: stac-pydantic [OPTIONS] COMMAND [ARGS]...

  stac-pydantic cli group

Options:
  --help  Show this message and exit.

Commands:
  validate-item  Validate STAC Item
```
