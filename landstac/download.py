# landstac/download.py
"""
Download helpers for LandsatLook asset HREFs.

This module provides small, focused functions to stream protected assets
to disk using an authenticated requests.Session. It does not print or log
credentials. Create the session via landstac.auth and pass it in.

Functions
---------
download_asset(href, session, out_path, chunk=1<<20)
    Stream one asset to a local GeoTIFF.
download_item_bands(item, session, bands, out_dir)
    Download several bands for a single STAC item into a scene folder.
stack_bands_to_geotiff(band_paths, out_path, order=None)
    Stack single-band GeoTIFFs into a single multiband GeoTIFF.

Examples
--------
>>> # sess = ers_login_from_file("credentials.json")
>>> # files = download_item_bands(item, sess, ["blue","green","red"], "downloads")
>>> # stack_bands_to_geotiff(files, "downloads/scene_stack.tif", order=["blue","green","red"])
"""

from __future__ import annotations
import os
from typing import Dict, Iterable
import requests
import rasterio
from .exceptions import DownloadError

def download_asset(href: str, session: requests.Session, out_path: str, chunk: int = 1 << 20) -> str:
    """
    Stream an asset to disk using an authenticated session.

    Parameters
    ----------
    href : str
        Remote asset URL from item.assets[band].href.
    session : requests.Session
        Authenticated ERS session. Do not embed credentials in code.
    out_path : str
        Local GeoTIFF path to write.
    chunk : int
        Chunk size in bytes for streaming.

    Returns
    -------
    str
        The local path written.

    Raises
    ------
    DownloadError
        On HTTP errors or authorization failures.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    try:
        with session.get(href, stream=True, timeout=120) as r:
            if r.status_code in (401, 403):
                raise DownloadError("Unauthorized. ERS session invalid or expired.")
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for part in r.iter_content(chunk):
                    if part:
                        f.write(part)
    except Exception as e:
        raise DownloadError(f"Failed to download {href}: {e}") from e
    return out_path


def download_item_bands(item, session: requests.Session, bands: Iterable[str], out_dir: str) -> Dict[str, str]:
    """
    Download selected bands for a STAC item.

    Parameters
    ----------
    item : pystac.Item
        STAC item from LandsatLook.
    session : requests.Session
        Authenticated session to access protected assets.
    bands : Iterable[str]
        Asset keys to download, for example ["blue","green","red","nir08"].
    out_dir : str
        Root folder to save files. A per-scene subfolder is created.

    Returns
    -------
    dict
        Mapping {band_name: local_path} for the bands that were downloaded.
    """
    scene = item.properties.get("landsat:scene_id", item.id)
    base = os.path.join(out_dir, scene)
    out: Dict[str, str] = {}
    for b in bands:
        if b not in item.assets:
            continue
        href = item.assets[b].href
        path = os.path.join(base, f"{scene}_{b}.tif")
        out[b] = download_asset(href, session, path)
    return out


def stack_bands_to_geotiff(band_paths: Dict[str, str], out_path: str, order: Iterable[str] | None = None) -> str:
    """
    Stack single-band GeoTIFFs into a multiband GeoTIFF.

    All input rasters must share identical CRS, transform, width, and height.

    Parameters
    ----------
    band_paths : dict
        Mapping {band_name: local_path} for single-band GeoTIFFs.
    out_path : str
        Destination path for the stacked GeoTIFF.
    order : Iterable[str], optional
        Desired band order. Defaults to sorted keys of band_paths.

    Returns
    -------
    str
        Path to the written multiband GeoTIFF.

    Raises
    ------
    ValueError
        If georeferencing does not match across inputs.
    """
    if not band_paths:
        raise ValueError("No band paths provided")
    order = list(order) if order else sorted(band_paths.keys())

    first = band_paths[order[0]]
    with rasterio.open(first) as src0:
        profile = src0.profile.copy()
        profile.update(count=len(order), compress="deflate", predictor=2,
                       tiled=True, blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER")
        transform = src0.transform
        crs = src0.crs

    with rasterio.open(out_path, "w", **profile) as dst:
        for i, k in enumerate(order, start=1):
            with rasterio.open(band_paths[k]) as src:
                if src.transform != transform or src.crs != crs:
                    raise ValueError("Band georeferencing mismatch")
                dst.write(src.read(1), i)
                dst.set_band_description(i, k)
    return out_path
