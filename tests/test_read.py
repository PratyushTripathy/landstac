import os
import numpy as np
import landstac as ls

def test_read_stac_bands_from_href(item_with_local_bands):
    # No session, no cache: open local HREFs directly
    arrs = ls.read_stac_bands(item_with_local_bands, bands=["blue","green"])
    assert set(arrs.keys()) == {"blue","green"}
    b = arrs["blue"]
    g = arrs["green"]
    assert b.shape[-2:] == g.shape[-2:]
    assert b.rio.crs is not None

def test_read_stac_bands_download_dir(tmp_path, item_with_local_bands, bytes_of):
    # Make an item whose HREFs are "remote" URLs
    scene = item_with_local_bands.properties["landsat:scene_id"]
    # Use the content of our local files as "server bytes"
    blue_local = item_with_local_bands.assets["blue"].href
    green_local = item_with_local_bands.assets["green"].href
    url_blue = "https://server/blue.tif"
    url_green = "https://server/green.tif"
    item = type(item_with_local_bands)(
        scene,
        {"blue": url_blue, "green": url_green}
    )

    payloads = {
        url_blue: bytes_of(blue_local),
        url_green: bytes_of(green_local),
    }
    FakeSession = __import__("tests.conftest", fromlist=["FakeSession"]).FakeSession
    sess = FakeSession(payloads)

    cache = tmp_path / "cache"
    arrs = ls.read_stac_bands(item, bands=["blue","green"], session=sess, download_dir=str(cache))
    # files should now exist on disk
    assert any(p.name.endswith("blue.tif") for p in (cache / scene).iterdir())
    assert "blue" in arrs and "green" in arrs

def test_read_stac_bands_in_memory(tmp_path, dB_tif):
    # Create an item pointing at a "remote" URL; session returns dB_tif bytes
    url = "https://server/db.tif"
    scene = "SCENE_DB"
    item = __import__("tests.conftest", fromlist=["DummyItem"]).DummyItem(scene, {"vv": url})

    with open(dB_tif, "rb") as f:
        payload = f.read()
    FakeSession = __import__("tests.conftest", fromlist=["FakeSession"]).FakeSession
    sess = FakeSession({url: payload})

    arrs = ls.read_stac_bands(item, bands=["vv"], session=sess, in_memory=True, to_linear=True)
    vv = arrs["vv"]
    # All values were 10 dB -> linear 10
    vals = vv.values
    assert np.isfinite(vals).all()
    # Allow tiny float tolerance
    assert np.allclose(vals[~np.isnan(vals)], 10.0, atol=1e-6)
