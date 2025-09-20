landstac Documentation
======================

Search and download Landsat imagery from USGS with Python.

``landstac`` connects to the USGS LandsatLook STAC API to search Landsat Collection 2 data and download protected assets with authentication.

Core capabilities
-----------------

- **Search**: Find Landsat scenes by location, date, and cloud cover
- **Authenticate**: Handle USGS login automatically
- **Download**: Get individual bands or full scenes
- **Stack**: Combine bands into multi-band GeoTIFFs
- **Stream**: Access data without downloading via GDAL integration

Available Collections
---------------------

The LandsatLook STAC API provides access to Landsat Collection 2 datasets:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Collection ID
     - Product Level
     - Description
   * - ``landsat-c2l1``
     - Level-1
     - TOA reflectance and brightness temperature
   * - ``landsat-c2l2-sr``
     - Level-2 UTM
     - Surface Reflectance (SR) Product
   * - ``landsat-c2l2-st``
     - Level-2 UTM
     - Surface Temperature (ST) Product
   * - ``landsat-c2l2alb-sr``
     - Level-2 Albers
     - Albers Surface Reflectance (SR) Product
   * - ``landsat-c2l2alb-st``
     - Level-2 Albers
     - Albers Surface Temperature (ST) Product
   * - ``landsat-c2l2alb-bt``
     - Level-2 Albers
     - Albers Top of Atmosphere Brightness Temperature (BT) Product
   * - ``landsat-c2l2alb-ta``
     - Level-2 Albers
     - Albers Top of Atmosphere (TA) Reflectance Product
   * - ``landsat-c2l3-fsca``
     - Level-3
     - Fractional Snow Covered Area (fSCA) Product
   * - ``landsat-c2l3-ba``
     - Level-3
     - Burned Area (BA) Product
   * - ``landsat-c2l3-dswe``
     - Level-3
     - Dynamic Surface Water Extent (DSWE) Product
   * - ``landsat-c2ard-sr``
     - ARD
     - Analysis Ready Data Surface Reflectance (SR) Product
   * - ``landsat-c2ard-st``
     - ARD
     - Analysis Ready Data Surface Temperature (ST) Product
   * - ``landsat-c2ard-bt``
     - ARD
     - Analysis Ready Data Top of Atmosphere Brightness Temperature (BT) Product
   * - ``landsat-c2ard-ta``
     - ARD
     - Analysis Ready Data Top of Atmosphere (TA) Reflectance Product

For an updated list of available collections, visit: https://stacindex.org/catalogs/usgs-landsat-collection-2-api

Supported sensors include Landsat 4-5 TM, Landsat 7 ETM+, Landsat 8 OLI/TIRS, and Landsat 9 OLI-2/TIRS-2.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   examples
   api

Getting Started
---------------

Install the package and start searching Landsat data:

.. code-block:: bash

   pip install landsatlook-stac

.. code-block:: python

   import landstac

   stac = landstac.LandsatLookSTAC()
   items = stac.search(
       collections=["landsat-c2l2-sr"],
       max_items=10
   )

See the :doc:`installation` guide for detailed setup instructions and the :doc:`examples` page for comprehensive usage examples.

Support & Contact
-----------------

**Author**: Pratyush Tripathy

Found a bug or have a feature request? Please report issues on the `GitHub Issues page <https://github.com/PratyushTripathy/landstac/issues>`_.

Contributions and feedback are welcome!

Quick Links
-----------

* **STAC Browser**: https://landsatlook.usgs.gov/stac-browser/
* **Collection Catalog**: https://stacindex.org/catalogs/usgs-landsat-collection-2-api
* **USGS ERS Registration**: https://ers.cr.usgs.gov/register/