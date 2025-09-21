# landstac

[![PyPI](https://img.shields.io/pypi/v/landsatlook-stac.svg)](https://pypi.org/project/landsatlook-stac/)
[![Docs](https://readthedocs.org/projects/landstac/badge/?version=latest)](https://landstac.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Import name:** `landstac`

Search and download Landsat imagery from USGS with Python.

## What it does

`landstac` connects to the USGS LandsatLook STAC API to search Landsat Collection 2 data and download protected assets with authentication.

## Core capabilities

- **Search**: Find Landsat scenes by location, date, and cloud cover
- **Authenticate**: Handle USGS login automatically
- **Download**: Get individual bands or full scenes
- **Stack**: Combine bands into multi-band GeoTIFFs
- **Stream**: Access data without downloading via GDAL integration

## Installation

```bash
pip install landsatlook-stac
```

## Documentation

**Full documentation:** https://landstac.readthedocs.io/

- [Installation guide](https://landstac.readthedocs.io/en/latest/installation.html)
- [Examples and tutorials](https://landstac.readthedocs.io/en/latest/examples.html)
- [API reference](https://landstac.readthedocs.io/en/latest/api.html)

## Support

**Author**: Pratyush Tripathy

Found a bug or have a feature request? Please report issues on the [GitHub Issues page](https://github.com/PratyushTripathy/landstac/issues).

Contributions and feedback are welcome!