Examples
========

This page provides a step-by-step guide to using ``landstac`` for Landsat data access workflows.

1. Search for Data
------------------

Start by searching for Landsat scenes and examining what a typical search returns:

.. code-block:: python

   import landstac as ls
   from landstac.utils import bbox_tuple, bbox_to_geojson

   # Define your area of interest (Las Vegas, Nevada)
   bbox = bbox_tuple(-115.359, 35.6763, -113.6548, 36.4831)
   geo = bbox_to_geojson(bbox)

   # Initialize STAC client and search
   stac = ls.LandsatLookSTAC()
   items = stac.search(
       collections=["landsat-c2l2-sr"],
       intersects=geo,
       datetime="2020-06-01/2020-08-31",
       query={"eo:cloud_cover": {"lte": 10}},
       max_items=3,
   )

   print(f"Found {len(items)} scenes")

   # Print basic details of top 3 items
   for i, item in enumerate(items):
       print(f"\nScene {i+1}:")
       print(f"  ID: {item.id}")
       print(f"  Date: {item.datetime}")
       print(f"  Cloud cover: {item.properties.get('eo:cloud_cover', 'N/A')}%")
       print(f"  Collection: {item.collection_id}")
       print(f"  Available bands: {len(item.assets)} bands")
       print(f"  Sample bands: {list(item.assets.keys())[:8]}...")

**Example output:**

.. code-block:: text

   Found 3 scenes

   Scene 1:
     ID: LC08_L2SP_038035_20200831_20200906_02_T1_SR
     Date: 2020-08-31 18:09:32.852535+00:00
     Cloud cover: 2.43%
     Collection: landsat-c2l2-sr
     Available bands: 17 bands
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'coastal', 'blue', 'green', 'red']...

   Scene 2:
     ID: LE07_L2SP_039035_20200830_20200925_02_T1_SR
     Date: 2020-08-30 17:42:30.160759+00:00
     Cloud cover: 0%
     Collection: landsat-c2l2-sr
     Available bands: 17 bands
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'blue', 'green', 'red', 'nir08']...

   Scene 3:
     ID: LC08_L2SP_040035_20200829_20200906_02_T1_SR
     Date: 2020-08-29 18:21:53.564774+00:00
     Cloud cover: 9.43%
     Collection: landsat-c2l2-sr
     Available bands: 17 bands
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'coastal', 'blue', 'green', 'red']...

You can modify the search by changing collections, date ranges, cloud cover thresholds, or spatial filters. While you can search and view metadata without authentication, to download the actual imagery you need to authenticate.

2. Authentication
-----------------

To download protected Landsat assets, you need USGS ERS authentication:

.. code-block:: python

   from landstac.auth import ers_login_from_file

   # Create credentials.json file (keeps credentials out of your code):
   # {
   #   "username": "your_usgs_username",
   #   "password": "your_usgs_password",
   #   "token": null
   # }

   session = ers_login_from_file("credentials.json")

3. Read Files in Memory
-----------------------

Once authenticated, read bands directly into memory and examine their properties:

.. code-block:: python

   from landstac.read import read_stac_bands

   # Read bands into xarray DataArrays
   data_arrays = read_stac_bands(
       item=items[0],
       bands=["nir08", "red", "green"],
       session=session,
       in_memory=True
   )

   # Print basic details like shape, number of bands
   for band_name, array in data_arrays.items():
       print(f"\n{band_name.upper()} band:")
       print(f"  Shape: {array.shape}")
       print(f"  CRS: {array.rio.crs}")
       print(f"  Data type: {array.dtype}")

   print(f"\nTotal bands loaded: {len(data_arrays)}")

**Example output:**

.. code-block:: text

   NIR08 band:
     Shape: (1, 7941, 7811)
     CRS: EPSG:32612
     Data type: uint16

   RED band:
     Shape: (1, 7941, 7811)
     CRS: EPSG:32612
     Data type: uint16

   GREEN band:
     Shape: (1, 7941, 7811)
     CRS: EPSG:32612
     Data type: uint16

   Total bands loaded: 3

4. Read with Overview
---------------------

Compare native resolution vs overview levels to see the difference:

.. code-block:: python

   # Read at overview level 2 (1/4 resolution)
   overview_res = read_stac_bands(
       item=items[0],
       bands=["nir08"],
       session=session,
       overview_level=2,
       in_memory=True
   )

   print("\nResolution comparison:")
   print(f"Native resolution: {data_arrays['nir08'].shape}")
   print(f"Overview level 2: {overview_res['nir08'].shape}")

   native_size = data_arrays['nir08'].size
   overview_size = overview_res['nir08'].size
   print(f"Overview is {native_size / overview_size:.1f}x smaller")

**Example output:**

.. code-block:: text

   Resolution comparison:
   Native resolution: (1, 7941, 7811)
   Overview level 2: (1, 993, 977)
   Overview is 63.9x smaller

5. Export Files to Drive
------------------------

Download and save bands as files on disk:

.. code-block:: python

   from landstac.download import download_item_bands, stack_bands_to_geotiff

   # Download specific bands to disk
   band_files = download_item_bands(
       item=items[0],
       session=session,
       bands=["nir08", "red", "green"],
       out_dir="landsat_data"
   )

   print(f"Downloaded files:")
   for band, path in band_files.items():
       print(f"  {band}: {path}")

   # Stack bands into a single multi-band GeoTIFF
   output_path = stack_bands_to_geotiff(
       band_paths=band_files,
       out_path="landsat_data/nrg_composite.tif",
       order=["nir08", "red", "green"]
   )

   print(f"\nStacked composite saved to: {output_path}")

**Example output:**

.. code-block:: text

   Downloaded files:
     nir08: landsat_data/LC80380352020244LGN00/LC80380352020244LGN00_nir08.tif
     red: landsat_data/LC80380352020244LGN00/LC80380352020244LGN00_red.tif
     green: landsat_data/LC80380352020244LGN00/LC80380352020244LGN00_green.tif

   Stacked composite saved to: landsat_data/nrg_composite.tif

6. Working with Multiple Collections
------------------------------------

Search across different Landsat product types:

.. code-block:: python

   # Search multiple collections
   multi_items = stac.search(
       collections=[
           "landsat-c2l2-sr",   # Surface Reflectance
           "landsat-c2l2-st",   # Surface Temperature
           "landsat-c2l1"       # Level-1 (TOA)
       ],
       intersects=geo,
       datetime="2020-06-01/2020-08-31",
       query={"eo:cloud_cover": {"lte": 20}},
       max_items=20
   )

   # Group results by collection
   by_collection = {}
   for item in multi_items:
       collection = item.collection_id
       if collection not in by_collection:
           by_collection[collection] = []
       by_collection[collection].append(item)

   # Show what's available in each collection
   for collection, items_list in by_collection.items():
       print(f"{collection}: {len(items_list)} scenes")
       if items_list:
           sample_bands = list(items_list[0].assets.keys())[:5]
           print(f"  Sample bands: {sample_bands}...")

**Example output:**

.. code-block:: text

   landsat-c2l2-st: 7 scenes
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'TRAD']...
   landsat-c2l2-sr: 7 scenes
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'coastal']...
   landsat-c2l1: 6 scenes
     Sample bands: ['thumbnail', 'reduced_resolution_browse', 'index', 'MTL.json', 'coastal']...

7. Working with Utility Functions
---------------------------------

Helper functions for geometry handling:

.. code-block:: python

   from landstac.utils import bbox_tuple, bbox_to_geojson, ee_polygon_to_bbox

   # Create bounding box from coordinates
   bbox = bbox_tuple(-120.5, 35.0, -119.5, 36.0)
   print(f"Bounding box: {bbox}")

   # Convert to GeoJSON for STAC searches
   geojson = bbox_to_geojson(bbox)
   print(f"GeoJSON type: {geojson['type']}")
   print(f"Coordinates: {geojson['coordinates']}")

   # Convert Earth Engine polygon coordinates to bbox
   ee_coords = [[[-120.5, 35.0], [-119.5, 35.0], [-119.5, 36.0], [-120.5, 36.0]]]
   converted_bbox = ee_polygon_to_bbox(ee_coords)
   print(f"Converted bbox: {converted_bbox}")

**Example output:**

.. code-block:: text

   Bounding box: (-120.5, 35.0, -119.5, 36.0)
   GeoJSON type: Polygon
   Coordinates: [[[-120.5, 35.0], [-120.5, 36.0], [-119.5, 36.0], [-119.5, 35.0], [-120.5, 35.0]]]
   Converted bbox: (-120.5, 35.0, -119.5, 36.0)

**Example output:**

.. code-block:: text

   Bounding box: (-120.5, 35.0, -119.5, 36.0)
   GeoJSON type: Polygon
   Coordinates: [[[-120.5, 35.0], [-120.5, 36.0], [-119.5, 36.0], [-119.5, 35.0], [-120.5, 35.0]]]
   Converted bbox: (-120.5, 35.0, -119.5, 36.0)