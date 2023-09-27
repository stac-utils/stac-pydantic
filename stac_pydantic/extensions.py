import json
from typing import Any, Dict, Union

import jsonschema
import requests

from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item


def validate_extensions(
    stac_obj: Union[Item, Collection, Catalog, Dict[str, Any]],
    reraise_exception: bool = False,
) -> bool:
    if isinstance(stac_obj, dict):
        stac_dict = stac_obj
    else:
        # can't use `stac_obj.model_dump()` here
        # b/c jsonschema expects pure string representations, not python types
        stac_dict = json.loads(stac_obj.model_dump_json())

    try:
        if stac_dict["stac_extensions"]:
            for ext in stac_dict["stac_extensions"]:
                req = requests.get(ext)
                schema = req.json()
                jsonschema.validate(instance=stac_dict, schema=schema)
    except Exception:
        if reraise_exception:
            raise
        return False
    return True
