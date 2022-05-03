from typing import Union

import jsonschema
import requests

from stac_pydantic import Catalog, Collection, Item


def validate_extensions(
    stac_obj: Union[Item, Collection, Catalog, dict], reraise_exception: bool = False
) -> bool:
    if isinstance(stac_obj, dict):
        stac_dict = stac_obj
    else:
        stac_dict = stac_obj.dict()

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
