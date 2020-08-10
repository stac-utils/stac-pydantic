# stac-pydantic ![tests](https://github.com/arturo-ai/stac-pydantic/workflows/cicd/badge.svg)
[Pydantic](https://pydantic-docs.helpmanual.io/) models for [STAC](https://github.com/radiantearth/stac-spec) Catalogs, Collections, Items, and the [STAC API](https://github.com/radiantearth/stac-api-spec) spec.

## Installation
```python
pip install stac-pydantic
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
STAC defines many extensions which let the user customize the data in their catalog.  Extensions can be validated
implicitly or explicitly:

#### Implicit
The `item_model_factory` function creates an appropriate Pydantic model based on the structure of the item by looking
at the extensions defined by the `stac_extensions` member.  The model can be created once and reused for the life of
the interpreter.

```python
from stac_pydantic import item_model_factory

stac_item = {
    "type": "Feature",
    "stac_extensions": [
        "eo"
    ],
    "geometry": ...,
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
        "eo:gsd": 0.15,
        "eo:cloud_cover": 17
    },
    "links": ...,
    "assets": ...,
}

model = item_model_factory(stac_item)
item = model(**stac_item)

>>> pydantic.error_wrappers.ValidationError: 1 validation error for Item
    __root__ -> properties -> eo:bands
        field required (eo) (type=value_error.missing)
```

The `stac_pydantic.validate_item` function provides a convenience wrapper over `item_model_factory` for one-off validation:

```python
from stac_pydantic import validate_item

assert validate_item(stac_item)
```

#### Explicit
Subclass any of the models provided by the library to declare a customized validator:

```python
from stac_pydantic import Item, ItemProperties, Extensions

class CustomProperties(Extensions.view, ItemProperties):
    ...

class CustomItem(Item):
    properties: CustomProperties # Override properties model

stac_item = {
    "type": "Feature",
    "geometry": ...,
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
        "view:off_nadir": 3.78,
    },
    "links": ...,
    "assets": ...,
}

item = CustomItem(**stac_item)
assert item.properties.off_nadir == 3.78
```

#### Vendor Extensions
STAC allows 3rd parties to define their own extensions for specific implementations which aren't currently covered by
the available content extensions.  You can validate vendor extensions in a similar fashion:
```python
from pydantic import BaseModel
from stac_pydantic import Extensions, Item

# 1. Create a model for the extension
class LandsatExtension(BaseModel):
    row: int
    column: int
    
    # Setup extension namespace in model config
    class Config:
        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"landsat:{field_name}"

# 2. Register the extension
Extensions.register("landsat", LandsatExtension)

# 3. Use model as normal
stac_item = {
    "type": "Feature",
    "stac_extensions": [
        "landsat",
        "view"
],
    "geometry": ...,
    "properties": {
        "datetime": "2020-03-09T14:53:23.262208+00:00",
        "view:off_nadir": 3.78,
        "landsat:row": 230,
        "landsat:column": 178 
    },
    "links": ...,
    "assets": ...,
}

item = Item(**stac_item)
assert item.properties.row == 230
assert item.properties.column == 178
```
Vendor extensions are often defined in `stac_extensions` as a [remote reference](https://github.com/radiantearth/stac-spec/blob/v0.9.0/item-spec/examples/landsat8-sample.json#L6) to a JSON schema.  When registering extensions, you may use the `alias` kwarg to 
indicate that the model represents a specific remote reference:

```python
Extensions.register("landsat", LandsatExtension, alias="https://example.com/stac/landsat-extension/1.0/schema.json")
```

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

## Testing
```python setup.py test```