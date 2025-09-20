"""
landstac

Short import for the landsatlook-stac project.
Search LandsatLook STAC and access protected assets via ERS auth.

Public API re-exports live here so users can do:
    import landstac as ls
    ls.LandsatLookSTAC(...)
"""

from .auth import ers_login, ers_login_from_file, make_session, save_cookies_for_gdal
from .stac import LandsatLookSTAC
from .download import download_asset, download_item_bands, stack_bands_to_geotiff
from .read import read_stac_bands
from .utils import bbox_to_geojson, ee_polygon_to_bbox, bbox_tuple
from .exceptions import AuthError, DownloadError, StacError

__all__ = [
    "ers_login", "ers_login_from_file", "make_session", "save_cookies_for_gdal",
    "LandsatLookSTAC",
    "download_asset", "download_item_bands", "stack_bands_to_geotiff",
    "read_stac_bands",
    "bbox_to_geojson", "ee_polygon_to_bbox", "bbox_tuple",
    "AuthError", "DownloadError", "StacError",
]

__version__ = "0.1.0"
