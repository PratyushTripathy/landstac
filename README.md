# landsatlook-stac

Install with pip, import as `landstac`.

## Install
pip install landsatlook-stac

## Quick start

```python
import landstac as ls
from landstac.utils import bbox_tuple, bbox_to_geojson

bbox = bbox_tuple(-115.359, 35.6763, -113.6548, 36.4831)
geo = bbox_to_geojson(bbox)

stac = ls.LandsatLookSTAC()
items = stac.search(
    collections=["landsat-c2l2-sr"],
    intersects=geo,
    datetime="1995-01-01/1995-12-31",
    query={"eo:cloud_cover": {"lte": 10}},
    max_items=5
)

sess = ls.ers_login_from_file("credentials.json")

bands = ["blue","green","red","nir08"]
files = ls.download_item_bands(items[0], sess, bands=bands, out_dir="data/landsat_sr_1995")
scene = items[0].properties.get("landsat:scene_id", items[0].id)
out_stack = f"data/landsat_sr_1995/{scene}_stack.tif"
ls.stack_bands_to_geotiff(files, out_stack, order=bands)
