# landstac/utils.py
"""
Utility helpers for geometry conversion and normalization.

Functions
---------
bbox_tuple(min_lon, min_lat, max_lon, max_lat)
    Return a strict (min_lon, min_lat, max_lon, max_lat) tuple of floats.
bbox_to_geojson(bbox)
    Convert a bbox tuple to a GeoJSON Polygon suitable for STAC searches.
ee_polygon_to_bbox(ee_coords)
    Convert an Earth Engine style polygon coordinate array to a bbox tuple.

Notes
-----
- All longitudes and latitudes are treated as WGS84 degrees.
- The GeoJSON Polygon returned by bbox_to_geojson is closed, with the last
  coordinate repeating the first.
"""

from __future__ import annotations
from typing import List
from .types import BBox, GeoJSON

def bbox_tuple(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> BBox:
    """
    Normalize and return a bounding box tuple.

    Parameters
    ----------
    min_lon, min_lat, max_lon, max_lat : float
        Bounding values in degrees.

    Returns
    -------
    BBox
        (min_lon, min_lat, max_lon, max_lat) as floats.

    Examples
    --------
    >>> bbox_tuple(-115.359, 35.6763, -113.6548, 36.4831)
    (-115.359, 35.6763, -113.6548, 36.4831)
    """
    return (float(min_lon), float(min_lat), float(max_lon), float(max_lat))


def bbox_to_geojson(bbox: BBox) -> GeoJSON:
    """
    Convert a bbox to a GeoJSON Polygon.

    Parameters
    ----------
    bbox : BBox
        Tuple in (min_lon, min_lat, max_lon, max_lat) order.

    Returns
    -------
    GeoJSON
        GeoJSON Polygon mapping.

    Examples
    --------
    >>> bbox_to_geojson((-1.0, -2.0, 3.0, 4.0))["type"]
    'Polygon'
    """
    minx, miny, maxx, maxy = bbox
    coords = [[
        [minx, miny],
        [minx, maxy],
        [maxx, maxy],
        [maxx, miny],
        [minx, miny],
    ]]
    return {"type": "Polygon", "coordinates": coords}


def ee_polygon_to_bbox(ee_coords: List[List[List[float]]]) -> BBox:
    """
    Convert an Earth Engine style polygon to a bbox tuple.

    Parameters
    ----------
    ee_coords : list
        Coordinates in the form [[ [lon, lat], [lon, lat], ... ]].
        Only the exterior ring is required, but additional rings are ignored safely.

    Returns
    -------
    BBox
        (min_lon, min_lat, max_lon, max_lat)

    Examples
    --------
    >>> ring = [[-52.7897, -10.7120], [-52.7897, -10.7200], [-52.7813, -10.7200], [-52.7813, -10.7120]]
    >>> ee_polygon_to_bbox([ring])
    (-52.7897, -10.72, -52.7813, -10.712)
    """
    xs, ys = [], []
    for ring in ee_coords:
        for lon, lat in ring:
            xs.append(lon)
            ys.append(lat)
    return (min(xs), min(ys), max(xs), max(ys))
