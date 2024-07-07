import json
from functools import lru_cache
from typing import Any, Dict, Union

import jsonschema
import requests

from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item


@lru_cache(maxsize=128)
def _fetch_schema(url: str) -> dict:
    """Fetch the remote JSON schema, if not already cached."""
    req = requests.get(url)
    return req.json()


def validate_extensions(
    stac_obj: Union[Item, Collection, Catalog, Dict[str, Any]],
    reraise_exception: bool = False,
) -> bool:
    """
    Fetch the remote JSON schema, if not already cached, and validate the STAC
    object against that schema.
    """
    if isinstance(stac_obj, dict):
        stac_dict = stac_obj
    else:
        # can't use `stac_obj.model_dump()` here
        # b/c jsonschema expects pure string representations, not python types
        stac_dict = json.loads(stac_obj.model_dump_json())

    try:
        if stac_dict["stac_extensions"]:
            for ext in stac_dict["stac_extensions"]:
                schema = _fetch_schema(ext)
                jsonschema.validate(instance=stac_dict, schema=schema)
    except Exception:
        if reraise_exception:
            raise
        return False
    return True
