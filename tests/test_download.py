import os
import landstac as ls

def test_download_asset_ok(tmp_path):
    url = "http://example.com/file.tif"
    payload = b"ABC123"
    sess = __import__("tests.conftest", fromlist=["FakeSession"]).FakeSession({url: payload})
    out = tmp_path / "out.tif"
    path = ls.download_asset(url, sess, str(out))
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == payload

def test_download_asset_unauthorized(tmp_path):
    url = "http://example.com/secret.tif"
    payload = b"nope"
    sess = __import__("tests.conftest", fromlist=["FakeSession"]).FakeSession({url: payload}, status_code=401)
    try:
        ls.download_asset(url, sess, str(tmp_path / "o.tif"))
        assert False, "Expected DownloadError"
    except ls.DownloadError:
        pass

def test_download_item_bands_and_stack(tmp_path, item_with_local_bands):
    # we'll monkeypatch download_asset to just copy from local "href" path
    calls = []
    def fake_download(href, session, out_path, chunk=1<<20):
        import shutil
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        shutil.copyfile(href, out_path)
        calls.append((href, out_path))
        return out_path

    # Patch & run
    import landstac.download as dmod
    orig = dmod.download_asset
    dmod.download_asset = fake_download
    try:
        mapping = ls.download_item_bands(item_with_local_bands, session=None, bands=["blue","green","nir08"], out_dir=str(tmp_path))
        assert "blue" in mapping and "green" in mapping
        assert os.path.exists(mapping["blue"]) and os.path.exists(mapping["green"])

        # stack them in custom order
        out_stack = tmp_path / "stack.tif"
        ls.stack_bands_to_geotiff(mapping, str(out_stack), order=["green", "blue"])
        import rasterio
        with rasterio.open(out_stack) as src:
            assert src.count == 2
            assert src.descriptions[0] == "green"
            assert src.descriptions[1] == "blue"
    finally:
        dmod.download_asset = orig
