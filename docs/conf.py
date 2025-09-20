from __future__ import annotations
import os, sys
from pathlib import Path
import importlib

# -- Path setup: add repo root for autodoc -----------------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# -- Project info --------------------------------------------------------------
project = "landsatlook-stac"
author = "Pratyush Tripathy"
copyright = ""
# Robust version retrieval
try:
    import landstac as _ls
    release = getattr(_ls, "__version__", "0.0.0")
except Exception:
    try:
        from importlib.metadata import version
        release = version("landsatlook-stac")
    except Exception:
        release = "0.0.0"

# -- General config ------------------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",      # NumPy/Google docstrings
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_class_signature = "mixed"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": False,
    "inherited-members": False,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True

myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "substitution"]
myst_heading_anchors = 3

intersphinx_mapping = {
    "python":   ("https://docs.python.org/3", None),
    "rasterio": ("https://rasterio.readthedocs.io/en/latest/", None),
    "xarray":   ("https://docs.xarray.dev/en/stable/", None),
    "pystac":   ("https://pystac.readthedocs.io/en/stable/", None),
}


templates_path = ["_templates"]
exclude_patterns: list[str] = []

# -- HTML ----------------------------------------------------------------------
html_theme = "furo"
html_title = f"{project} {release}"
html_static_path = ["_static"]

# -- Options to make Markdown/rST play nice -----------------------------------
suppress_warnings = ["myst.xref_missing"]
