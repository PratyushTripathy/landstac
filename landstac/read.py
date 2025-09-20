# landstac/read.py
"""
Read helpers for opening STAC assets as xarray DataArrays.

Access modes
------------
1) Public HREFs: open directly with rioxarray.
2) Auth + cache: download to a cache dir, then open.
3) Auth + RAM: stream the whole asset into memory, no files on disk.

Notes
-----
- Native resolution by default: set `overview_level=None`.
- Internal overviews: pass an int overview level to read a lower-res pyramid.
- When `download_dir` is provided, assets are cached to:
    download_dir/<scene_id>/<filename>
"""

from __future__ import annotations
import os
import io
from typing import Dict, Iterable, Optional
import requests
import rioxarray as rxr
from rasterio.io import MemoryFile

def read_stac_bands(
    item,
    bands: Iterable[str] = ("blue", "green", "red", "nir08"),
    overview_level: Optional[int] = None,
    to_linear: bool = False,
    session: Optional[requests.Session] = None,
    download_dir: Optional[str] = None,
    in_memory: bool = False,
) -> Dict[str, "rxr.DataArray"]:
    """
    Open one or more STAC asset bands as rioxarray DataArrays.

    Parameters
    ----------
    item : pystac.Item
        STAC item.
    bands : Iterable[str]
        Asset keys to open (e.g., ["blue","green","red","nir08"]).
    overview_level : int or None
        None for native resolution; integer for an internal overview.
    to_linear : bool
        Apply 10**(x/10) conversion (e.g., Sentinel-1 dB -> linear).
    session : requests.Session, optional
        Authenticated ERS session. Required for protected assets if using
        `download_dir` or `in_memory`.
    download_dir : str, optional
        Cache directory; files are stored under
        `download_dir/<scene_id>/<filename>`.
    in_memory : bool
        If True, stream the full asset into RAM and open from memory file.

    Returns
    -------
    dict
        Mapping {band_name: DataArray}.
    """
    arrays: Dict[str, rxr.DataArray] = {}

    # ---------- Helpers ----------
    def _open_from_href(href: str):
        return rxr.open_rasterio(href, masked=True, overview_level=overview_level)

    def _open_from_disk(href: str, out_path: str):
        if not os.path.exists(out_path):
            if session is None:
                raise ValueError("session is required to download protected assets")
            with session.get(href, stream=True, timeout=120) as r:
                r.raise_for_status()
                os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        if chunk:
                            f.write(chunk)
        return rxr.open_rasterio(out_path, masked=True, overview_level=overview_level)

    def _open_in_memory(href: str):
        if session is None:
            raise ValueError("session is required for in_memory=True")
        r = session.get(href, stream=True, timeout=120)
        r.raise_for_status()
        bio = io.BytesIO()
        for chunk in r.iter_content(1 << 20):
            if chunk:
                bio.write(chunk)
        bio.seek(0)
        with MemoryFile(bio) as memfile:
            with memfile.open() as src:
                return rxr.open_rasterio(src, masked=True, overview_level=overview_level)
    # -----------------------------

    for b in bands:
        if b not in item.assets:
            continue
        href = item.assets[b].href

        if session is None and download_dir is None and not in_memory:
            # Public asset HREF
            da = _open_from_href(href)

        elif download_dir and not in_memory:
            # Cache under download_dir/<scene_id>/<filename>
            scene = item.properties.get("landsat:scene_id", item.id)
            scene_dir = os.path.join(download_dir, scene)
            os.makedirs(scene_dir, exist_ok=True)
            fname = os.path.basename(href)
            out_path = os.path.join(scene_dir, fname)
            da = _open_from_disk(href, out_path)

        else:
            # Auth + RAM
            da = _open_in_memory(href)

        if to_linear:
            da = 10 ** (da / 10.0)

        arrays[b] = da

    return arrays
