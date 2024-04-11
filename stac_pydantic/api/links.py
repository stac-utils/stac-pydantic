from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field

from stac_pydantic.links import Link
from stac_pydantic.links import Links as BaseLinks
from stac_pydantic.links import Relations
from stac_pydantic.shared import MimeTypes


class _MethodLink(Link):
    """
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#pagination
    """

    method: Literal["GET", "POST"] = "GET"
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[Any, Any]] = None
    merge: bool = False


class PaginationLink(_MethodLink):
    """
    https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md#pagination
    """

    rel: Literal[Relations.next, Relations.prev]


class SearchLink(_MethodLink):
    """
    https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/item-search#link-relations
    """

    href: str = Field(..., pattern=r".*\/search(\?.*)?\b")
    type: Literal[MimeTypes.geojson] = MimeTypes.geojson
    rel: Literal[Relations.self, Relations.search, Relations.next, Relations.prev]


class ItemsLink(_MethodLink):
    href: str = Field(..., pattern=r".*\/items(\?.*)?\b")
    type: Literal[MimeTypes.geojson] = MimeTypes.geojson
    rel: Literal[Relations.self, Relations.items]


class Links(BaseLinks):
    root: List[Union[SearchLink, PaginationLink, ItemsLink, Link]]
