from functools import singledispatch

import jsonschema
import requests

from stac_pydantic import Catalog, Collection, Item


@singledispatch
def validate_extensions(stac_obj, b):
    raise NotImplementedError("Unsupported type")


@validate_extensions.register
def _(stac_obj: dict, reraise_exception: bool = False, **kwargs) -> bool:
    try:
        if stac_obj["stac_extensions"]:
            for ext in stac_obj["stac_extensions"]:
                req = requests.get(ext)
                schema = req.json()
                jsonschema.validate(instance=stac_obj, schema=schema)
    except Exception:
        if reraise_exception:
            raise
        return False
    return True


@validate_extensions.register
def _(stac_obj: Item, reraise_exception: bool = False, **kwargs) -> bool:
    validate_extensions(stac_obj.dict(), reraise_exception)


@validate_extensions.register
def _(stac_obj: Collection, reraise_exception: bool = False, **kwargs) -> bool:
    validate_extensions(stac_obj.dict(), reraise_exception)


@validate_extensions.register
def _(stac_obj: Catalog, reraise_exception: bool = False, **kwargs) -> bool:
    validate_extensions(stac_obj.dict(), reraise_exception)
