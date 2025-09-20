"""
Thin wrapper around pystac-client for LandsatLook STAC.
"""

from typing import List, Dict, Any
from pystac_client import Client
from .exceptions import StacError

LANDSATLOOK_STAC = "https://landsatlook.usgs.gov/stac-server"

class LandsatLookSTAC:
    """
    Example:
        stac = LandsatLookSTAC()
        items = stac.search(
            collections=["landsat-c2l2-sr"],
            intersects=geojson,
            datetime="1995-01-01/1995-12-31",
            query={"eo:cloud_cover": {"lte": 10}},
            max_items=100
        )
    """
    def __init__(self, url: str = LANDSATLOOK_STAC):
        self.url = url
        self._client = Client.open(self.url)

    def search(
        self,
        collections: List[str] | None = None,
        intersects: Dict[str, Any] | None = None,
        datetime: str | None = None,
        query: Dict[str, Any] | None = None,
        max_items: int | None = None,
    ):
        try:
            s = self._client.search(
                collections=collections,
                intersects=intersects,
                datetime=datetime,
                query=query,
                max_items=max_items,
            )
            return list(s.get_items())
        except Exception as e:
            raise StacError(f"STAC search failed: {e}") from e
