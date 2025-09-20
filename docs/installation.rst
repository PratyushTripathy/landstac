Installation
============

Requirements
------------

* Python 3.8+
* Internet connection for STAC API access

Install from PyPI
-----------------

.. code-block:: bash

   pip install landsatlook-stac

Development Installation
------------------------

For development or to get the latest features:

.. code-block:: bash

   git clone https://github.com/your-username/landstac.git
   cd landstac
   pip install -e .

Dependencies
------------

``landstac`` automatically installs these required packages:

* ``pystac-client`` - STAC API client
* ``requests`` - HTTP library
* ``beautifulsoup4`` - HTML parsing for authentication
* ``rasterio`` - Geospatial raster I/O
* ``rioxarray`` - xarray integration for rasterio
* ``tqdm`` - Progress bars

Authentication Setup
--------------------

To access protected Landsat assets, you need a USGS ERS account:

1. Register at https://ers.cr.usgs.gov/register/
2. Create a ``credentials.json`` file in your working directory:

.. code-block:: json

   {
     "username": "your_usgs_username",
     "password": "your_usgs_password",
     "token": null
   }

Alternatively, set environment variables:

.. code-block:: bash

   export USGS_USER="your_username"
   export USGS_PASS="your_password"

Verification
------------

Test your installation:

.. code-block:: python

   import landstac

   stac = landstac.LandsatLookSTAC()
   print(f"Connected to: {stac.url}")

   # Test a simple search (no authentication required)
   items = stac.search(
       collections=["landsat-c2l2-sr"],
       max_items=1
   )
   print(f"Search successful: found {len(items)} item(s)")