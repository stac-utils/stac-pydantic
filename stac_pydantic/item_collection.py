from typing import Optional, Sequence

from geojson_pydantic import FeatureCollection

from stac_pydantic.item import Item
from stac_pydantic.links import Links
from stac_pydantic.shared import StacBaseModel


class ItemCollection(FeatureCollection, StacBaseModel):
    """
    This is a less strict implementation of ItemCollection.
    It only implements the FeatureCollection Specs
    not enforcing required links as specified in STAC-API-FEATURES specs.
    Use `stac_pydantic.api.ItemCollection` to enforce link relationships and extra fields.
    """

    features: Sequence[Item]  # type: ignore
    links: Optional[Links] = None
