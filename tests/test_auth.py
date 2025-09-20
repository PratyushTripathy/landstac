import os
import landstac as ls

def test_ers_login_from_file_missing(tmp_path):
    path = tmp_path / "nope.json"
    try:
        ls.ers_login_from_file(str(path))
        assert False, "Expected AuthError when credentials file is missing"
    except ls.AuthError:
        pass

def test_save_cookies_for_gdal(tmp_path):
    # Create a session with one cookie
    import requests
    sess = requests.Session()
    sess.cookies.set("ers_session", "abc123", domain="landsatlook.usgs.gov", path="/")
    cookie_file = ls.save_cookies_for_gdal(sess, cookiefile=str(tmp_path / "cookies.txt"))
    assert os.path.exists(cookie_file)
    # File should contain the cookie name somewhere
    with open(cookie_file, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    assert "ers_session" in txt
