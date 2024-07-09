from functools import lru_cache
from typing import Any, Dict, Union

from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item

try:
    import requests
except ImportError:  # pragma: nocover
    requests = None  # type: ignore

try:
    import jsonschema
except ImportError:  # pragma: nocover
    jsonschema = None  # type: ignore


@lru_cache(maxsize=128)
def _fetch_and_cache_schema(url: str) -> dict:
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
    assert requests is not None, "requests must be installed to validate extensions"
    assert jsonschema is not None, "jsonschema must be installed to validate extensions"

    if isinstance(stac_obj, dict):
        stac_dict = stac_obj
    else:
        stac_dict = stac_obj.model_dump(mode="json")

    try:
        if stac_dict["stac_extensions"]:
            for ext in stac_dict["stac_extensions"]:
                schema = _fetch_and_cache_schema(ext)
                jsonschema.validate(instance=stac_dict, schema=schema)
    except Exception:
        if reraise_exception:
            raise
        return False
    return True
