from dataclasses import dataclass
from typing import ClassVar, Tuple
from urllib.parse import urljoin

from stac_pydantic.links import Link, Links, Relations
from stac_pydantic.shared import MimeTypes


@dataclass
class BaseLinks:
    """Create inferred links common to collections and items."""

    base_url: str
    _link_members: ClassVar[Tuple[str]] = ("root",)

    def root(self) -> Link:
        """Return the catalog root."""
        return Link(
            rel=Relations.root, type=MimeTypes.json, href=urljoin(self.base_url, "/")
        )

    def create_links(self) -> Links:
        """Create inferred links"""
        return Links.parse_obj(
            [getattr(self, member)() for member in self._link_members]
        )


@dataclass
class CollectionLinks(BaseLinks):
    """Create inferred links specific to collections."""

    collection_id: str
    _link_members: ClassVar[Tuple[str]] = ("root", "self", "parent", "item")

    def self(self) -> Link:
        """Create the `self` link."""
        return Link(
            rel=Relations.self,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"/collections/{self.collection_id}"),
        )

    def parent(self) -> Link:
        """Create the `parent` link."""
        return Link(
            rel=Relations.parent, type=MimeTypes.json, href=urljoin(self.base_url, "/")
        )

    def item(self) -> Link:
        """Create the `item` link."""
        return Link(
            rel=Relations.item,
            type=MimeTypes.geojson,
            href=urljoin(self.base_url, f"/collections/{self.collection_id}/items"),
        )


@dataclass
class ItemLinks(BaseLinks):
    """Create inferred links specific to items."""

    collection_id: str
    item_id: str
    _link_members: ClassVar[Tuple[str]] = ("root", "self", "parent", "collection")

    def self(self) -> Link:
        """Create the `self` link."""
        return Link(
            rel=Relations.self,
            type=MimeTypes.geojson,
            href=urljoin(
                self.base_url, f"/collections/{self.collection_id}/items/{self.item_id}"
            ),
        )

    def parent(self) -> Link:
        """Create the `parent` link."""
        return Link(
            rel=Relations.parent,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"/collections/{self.collection_id}"),
        )

    def collection(self) -> Link:
        """Create the `collection` link."""
        return Link(
            rel=Relations.collection,
            type=MimeTypes.json,
            href=urljoin(self.base_url, f"/collections/{self.collection_id}"),
        )
