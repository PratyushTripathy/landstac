# tests/test_utils.py
import pytest
import landstac as ls

def test_bbox_to_geojson_and_back_specific():
    # Your bbox
    geo_bbox = (-115.359, 35.6763, -113.6548, 36.4831)

    # 1) Normalize via helper (ensures proper float types/order)
    bbox = ls.bbox_tuple(*geo_bbox)
    assert bbox == pytest.approx(geo_bbox)

    # 2) Convert to GeoJSON polygon and validate ring + extents
    geo = ls.bbox_to_geojson(bbox)
    assert geo["type"] == "Polygon"
    ring = geo["coordinates"][0]
    assert ring[0] == ring[-1], "Polygon ring must be closed"

    xs = [c[0] for c in ring[:-1]]
    ys = [c[1] for c in ring[:-1]]
    assert (min(xs), min(ys), max(xs), max(ys)) == pytest.approx(geo_bbox)


def test_ee_polygon_to_bbox_specific():
    # Build an EE-style polygon directly from your bbox
    geo_bbox = (-115.359, 35.6763, -113.6548, 36.4831)
    minx, miny, maxx, maxy = geo_bbox

    ee_coords = [[
        [minx, miny],
        [minx, maxy],
        [maxx, maxy],
        [maxx, miny],
        [minx, miny],  # closed ring (ok if you omit this; helper ignores closure)
    ]]

    bbox = ls.ee_polygon_to_bbox(ee_coords)
    assert bbox == pytest.approx(geo_bbox)
