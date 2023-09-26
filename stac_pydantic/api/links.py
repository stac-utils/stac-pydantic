from enum import auto
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from stac_pydantic.links import Link
from stac_pydantic.links import Links as BaseLinks
from stac_pydantic.links import Relations
from stac_pydantic.shared import MimeTypes
from stac_pydantic.utils import AutoValueEnum


class PaginationMethods(str, AutoValueEnum):
    """
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#http-request-methods-and-content-types
    """

    GET = auto()
    POST = auto()


class PaginationLink(Link):
    """
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#pagination
    """

    method: PaginationMethods = PaginationMethods.GET
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[Any, Any]] = None
    merge: bool = False

    # TODO: Why does MyPy wants me to declare it again?
    type: Optional[MimeTypes] = None

    @field_validator("rel")
    @classmethod
    def rel_value(cls, v: Relations) -> Relations:
        required_rel = [Relations.next, Relations.prev]
        if v not in required_rel:
            raise ValueError(f"Field `type` must be one of {required_rel}")
        return v


class SearchLink(PaginationLink):
    """
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/item-search#link-relations
    """

    href: str = Field(..., pattern=r".*\/search(\?.*)?\b")
    type: Optional[MimeTypes] = MimeTypes.geojson

    @field_validator("rel")
    @classmethod
    def rel_value(cls, v: Relations) -> Relations:
        required_rel = [
            Relations.self,
            Relations.search,
            Relations.next,
            Relations.prev,
        ]
        if v not in required_rel:
            raise ValueError(f"Field `type` must be one of {required_rel}")
        return v


class ItemsLink(Link):
    href: str = Field(..., pattern=r".*\/items(\?.*)?\b")
    type: Optional[MimeTypes] = MimeTypes.geojson

    @field_validator("rel")
    @classmethod
    def rel_value(cls, v: Relations) -> Relations:
        required_rel = [Relations.self, Relations.items]
        if v not in required_rel:
            raise ValueError(f"Field `type` must be one of {required_rel}")
        return v


class Links(BaseLinks):
    root: List[Union[SearchLink, PaginationLink, ItemsLink, Link]]
