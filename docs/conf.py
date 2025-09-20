# --- top of docs/conf.py ---
from importlib.metadata import version as pkg_version, PackageNotFoundError

project = "landsatlook-stac"
author = "Pratyush Tripathy"

try:
    release = pkg_version("landsatlook-stac")  # full version, e.g. 0.1.0
except PackageNotFoundError:
    release = "0.0.0"

# Sphinx expects `version` (short X.Y) to be a STRING
version = ".".join(release.split(".")[:2])     # e.g. "0.1"


extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

# mock heavy/geospatial deps so autodoc works on RTD
autodoc_mock_imports = [
    "rasterio", "rioxarray", "osgeo", "numpy",
    "pystac_client", "requests", "tqdm", "bs4",
]

autosummary_generate = True
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

intersphinx_mapping = {
    "python":   ("https://docs.python.org/3", None),
    "rasterio": ("https://rasterio.readthedocs.io/en/latest/", None),
    "xarray":   ("https://docs.xarray.dev/en/stable/", None),
    "pystac":   ("https://pystac.readthedocs.io/en/stable/", None),
}
html_theme = "furo"
