"""
Thin wrapper around pystac-client for querying the LandsatLook STAC API.

The LandsatLook STAC API provides access to Landsat Collection 2 metadata and
assets. This wrapper simplifies common search operations while raising clear
errors when requests fail.

For more information on available collections, see:
https://stacindex.org/catalogs/usgs-landsat-collection-2-api#/?t=0
"""

from typing import List, Dict, Any
from pystac_client import Client
from .exceptions import StacError

LANDSATLOOK_STAC = "https://landsatlook.usgs.gov/stac-server"

class LandsatLookSTAC:
    """
    A lightweight wrapper around the LandsatLook STAC API client.

    This class simplifies searches against the Landsat Collection 2 STAC catalog,
    allowing queries by collection, spatial geometry, temporal range, and
    attribute filters.

    Example:
        >>> stac = LandsatLookSTAC()
        >>> items = stac.search(
        ...     collections=["landsat-c2l2-sr"],
        ...     intersects=geojson,
        ...     datetime="1995-01-01/1995-12-31",
        ...     query={"eo:cloud_cover": {"lte": 10}},
        ...     max_items=100,
        ... )
        >>> len(items)
        25

    For an up-to-date list of available Landsat collections, visit:
    https://stacindex.org/catalogs/usgs-landsat-collection-2-api#/?t=0
    """

    def __init__(self, url: str = LANDSATLOOK_STAC):
        """
        Initialize a LandsatLook STAC client.

        Args:
            url (str, optional): Base URL of the STAC API.
                Defaults to the official LandsatLook STAC endpoint:
                "https://landsatlook.usgs.gov/stac-server"
        """
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
        """
        Search the LandsatLook STAC API.

        Args:
            collections (List[str], optional): One or more Landsat collections
                to search. Example: ["landsat-c2l2-sr"].
            intersects (Dict[str, Any], optional): A GeoJSON geometry used to
                spatially filter results.
            datetime (str, optional): An ISO 8601 time range for filtering.
                Example: "1995-01-01/1995-12-31".
            query (Dict[str, Any], optional): Additional STAC query parameters.
                Example: {"eo:cloud_cover": {"lte": 10}}.
            max_items (int, optional): Maximum number of items to return.

        Returns:
            List[pystac.Item]: A list of STAC Item objects matching the query.

        Raises:
            StacError: If the STAC search fails for any reason.
        """
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
