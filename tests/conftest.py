import io
import os
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

class DummyAsset:
    def __init__(self, href: str):
        self.href = href

class DummyItem:
    def __init__(self, scene_id: str, assets: dict):
        self.id = scene_id
        self.properties = {"landsat:scene_id": scene_id}
        self.assets = {k: DummyAsset(v) for k, v in assets.items()}

def _write_tif(path, width=8, height=6, value=1, crs="EPSG:4326", dtype="uint16"):
    # Simple geotransform: upper-left at (0,0), pixel size 0.1 deg
    transform = from_origin(0.0, 0.0, 0.1, 0.1)
    profile = {
        "driver": "GTiff",
        "width": width,
        "height": height,
        "count": 1,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "tiled": False,
    }
    data = np.full((height, width), value, dtype=np.dtype(dtype))
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data, 1)
    return path

@pytest.fixture
def tiny_tif(tmp_path):
    p = tmp_path / "tiny.tif"
    _write_tif(p, value=7)
    return str(p)

@pytest.fixture
def dB_tif(tmp_path):
    # Create a float32 raster with constant 10.0 (10 dB -> linear should be 10**(10/10)=10)
    p = tmp_path / "db.tif"
    _write_tif(p, value=10.0, dtype="float32")
    return str(p)

@pytest.fixture
def item_with_local_bands(tmp_path):
    blue = tmp_path / "scene_blue.tif"
    green = tmp_path / "scene_green.tif"
    _write_tif(blue, value=11)
    _write_tif(green, value=22)
    item = DummyItem(
        "SCENE_ABC",
        {"blue": str(blue), "green": str(green)},
    )
    return item

class FakeResp:
    """Minimal requests-like response for session.get(...) context manager."""
    def __init__(self, content: bytes, status_code: int = 200):
        self._content = content
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=1 << 20):
        # yield in chunks
        buf = io.BytesIO(self._content)
        while True:
            chunk = buf.read(chunk_size)
            if not chunk:
                break
            yield chunk

@pytest.fixture
def bytes_of(path_factory=lambda: None):
    # helper to read bytes from a local file into memory
    def _read_bytes(pth: str) -> bytes:
        with open(pth, "rb") as f:
            return f.read()
    return _read_bytes

class FakeSession:
    """requests.Session drop-in with programmable byte payloads per URL."""
    def __init__(self, mapping: dict[str, bytes], status_code: int = 200):
        self._map = mapping
        self._status = status_code
        self.headers = {}
        # cookiejar-like minimal surface (only used by save_cookies_for_gdal test)
        from requests.cookies import RequestsCookieJar
        self.cookies = RequestsCookieJar()

    def get(self, url, stream=True, timeout=120):
        content = self._map.get(url, b"")
        return FakeResp(content, status_code=self._status)
