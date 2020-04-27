from .assets import AssetExtension
from .commons import CommonsExtension
from .datacube import DatacubeExtension
from .eo import ElectroOpticalExtension
from .label import LabelExtension
from .pc import PointCloudExtension
from .proj import ProjectionExtension
from .sar import SARExtension
from .sat import SatelliteExtension
from .sci import ScientificExtension
from .version import VersionExtension
from .view import ViewExtension


class Extensions:
    asset = AssetExtension
    commons = CommonsExtension
    datacube = DatacubeExtension
    eo = ElectroOpticalExtension
    label = LabelExtension
    pointcloud = PointCloudExtension
    proj = ProjectionExtension
    sar = SARExtension
    sat = SatelliteExtension
    scientific = ScientificExtension
    version = VersionExtension
    view = ViewExtension

    aliases = {}

    @classmethod
    def register(cls, k, v, alias=None):
        setattr(cls, k, v)

        if alias:
            cls.aliases[alias] = k

    @classmethod
    def get(cls, k):
        try:
            return getattr(cls, k)
        except AttributeError:
            try:
                return getattr(cls, cls.aliases[k])
            except KeyError:
                raise AttributeError(f"Invalid extension name or alias: {k}")
