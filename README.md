# landsatlook-stac

[![PyPI](https://img.shields.io/pypi/v/landsatlook-stac.svg)](https://pypi.org/project/landsatlook-stac/)
[![Docs](https://readthedocs.org/projects/landstac/badge/?version=latest)](https://landstac.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Import name:** `landstac`  
LandsatLook STAC search + authenticated asset access (via USGS ERS), with handy readers for native-resolution COGs and simple band stacking.

---

## Install

```bash
pip install landsatlook-stac
```

## Quick start

```python
import landstac as ls
from landstac.utils import bbox_tuple, bbox_to_geojson

# AOI → GeoJSON (your example bbox)
bbox = bbox_tuple(-115.359, 35.6763, -113.6548, 36.4831)
geo = bbox_to_geojson(bbox)

# 1) Search LandsatLook STAC
stac = ls.LandsatLookSTAC()
items = stac.search(
    collections=["landsat-c2l2-sr"],
    intersects=geo,
    datetime="1995-01-01/1995-12-31",
    query={"eo:cloud_cover": {"lte": 10}},
    max_items=5,
)
assert items, "No items found"

# 2) Authenticate (USGS ERS). Keep this file local and out of version control.
sess = ls.ers_login_from_file("credentials.json")

# 3A) Read bands directly in memory (no files on disk), native resolution
arrs = ls.read_stac_bands(
    items[0],
    bands=["blue", "green", "red", "nir08"],
    session=sess,
    in_memory=True,          # stream into RAM
    overview_level=None,     # None = native res
)
blue = arrs["blue"]
print("Blue shape:", blue.shape, "res:", blue.rio.resolution(), "crs:", blue.rio.crs)

# 3B) Or cache to disk, then stack to a single GeoTIFF
out_map = ls.download_item_bands(
    items[0],
    session=sess,
    bands=["blue", "green", "red", "nir08"],
    out_dir="data/landsat_sr_1995",   # files saved under data/<scene_id>/
)
ls.stack_bands_to_geotiff(out_map, "data/landsat_sr_1995/stack.tif", order=["red", "green", "blue"])
