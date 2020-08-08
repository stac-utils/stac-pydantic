from typing import List

from pydantic import AnyHttpUrl, BaseModel


class ConformanceClasses(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#ogc-api---features-endpoints
    """

    conformsTo: List[AnyHttpUrl]
