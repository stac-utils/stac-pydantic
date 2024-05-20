from enum import auto
from typing import Iterator, List, Optional
from urllib.parse import urljoin

from pydantic import ConfigDict, Field, RootModel

from stac_pydantic.shared import MimeTypes, StacBaseModel
from stac_pydantic.utils import AutoValueEnum


class Link(StacBaseModel):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#link-object
    """

    href: str = Field(..., alias="href", min_length=1)
    rel: str = Field(..., alias="rel", min_length=1)
    type: Optional[MimeTypes] = None
    title: Optional[str] = None

    # Label extension
    label: Optional[str] = Field(default=None, alias="label:assets")
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    def resolve(self, base_url: str) -> None:
        """resolve a link to the given base URL"""
        self.href = urljoin(base_url, self.href)


class Links(RootModel[List[Link]]):
    root: List[Link]

    def link_iterator(self) -> Iterator[Link]:
        """Produce iterator to iterate through links"""
        return iter(self.root)

    def resolve(self, base_url: str) -> None:
        """resolve all links to the given base URL"""
        for link in self.link_iterator():
            link.resolve(base_url)

    def append(self, link: Link) -> None:
        self.root.append(link)

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, idx: int) -> Link:
        return self.root[idx]


class Relations(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#relation-types
    https://github.com/radiantearth/stac-spec/blob/v1.0.0/best-practices.md#using-relation-types
    """

    self = auto()
    root = auto()
    parent = auto()
    child = auto()
    children = auto()
    items = auto()
    license = auto()
    derived_from = auto()
    collection = auto()
    alternate = auto()
    previous = auto()
    prev = auto()
    next = auto()
    conformance = auto()
    docs = auto()
    tiles = auto()
    search = auto()
    preview = auto()
    canonical = auto()
    via = auto()
    data = auto()
    service_desc = "service-desc"
    service_doc = "service-doc"
    queryables = "http://www.opengis.net/def/rel/ogc/1.0/queryables"
