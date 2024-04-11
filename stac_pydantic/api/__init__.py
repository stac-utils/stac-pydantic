"""STAC API models."""

import warnings

from .collection import Collection
from .collections import Collections
from .conformance import Conformance
from .item import Item
from .item_collection import ItemCollection
from .landing import LandingPage
from .search import Search

__all__ = [
    "Collection",
    "Collections",
    "Conformance",
    "Item",
    "ItemCollection",
    "LandingPage",
    "Search",
]


# TODO: remove in 4.0
def __getattr__(name):
    if name == "ConformanceClasses":
        warnings.warn(
            "Class `ConformanceClasses` has been renamed to `Conformance`. Please use the new name. The old alias will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return Conformance

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
