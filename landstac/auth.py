"""
ERS authentication and session helpers.

Functions:
- make_session: create a requests.Session with retries and headers
- ers_login: log in to ERS (USGS) and return an authenticated session
- ers_login_from_file: read credentials.json and log in
- save_cookies_for_gdal: export session cookies to a Mozilla cookie file so
  GDAL/rasterio can stream protected assets without downloading
"""

from __future__ import annotations
import json, os, time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from http.cookiejar import MozillaCookieJar
from .types import Credentials
from .exceptions import AuthError

ERS_LOGIN_URL = "https://ers.cr.usgs.gov/login/"
USER_AGENT = "llstac/0.1 (+python-requests)"

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

def _submit_login_form(s: requests.Session, username: str, password: str) -> None:
    # Load login page to capture hidden inputs
    r = s.get(ERS_LOGIN_URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    if form is None:
        # Try direct post as fallback
        data = {"username": username, "password": password}
        r = s.post(ERS_LOGIN_URL, data=data, timeout=30, allow_redirects=True)
        r.raise_for_status()
        return

    data = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        data[name] = inp.get("value", "")
    data["username"] = username
    data["password"] = password

    action = form.get("action") or ERS_LOGIN_URL
    if action.startswith("/"):
        action = requests.compat.urljoin(ERS_LOGIN_URL, action)

    r = s.post(action, data=data, timeout=30, allow_redirects=True)
    r.raise_for_status()

def ers_login(username: str, password: str, token: str | None = None) -> requests.Session:
    """
    Log in to ERS and return an authenticated session.

    Args:
        username (str): USGS ERS username.
        password (str): USGS ERS password.
        token (str, optional): Optional bearer token for authorization header.

    Returns:
        requests.Session: Authenticated session with ERS cookies.

    Note:
        If token is provided and accepted by the host, it is attached as
        Authorization header.
    """
    s = make_session()
    _submit_login_form(s, username, password)
    # Heuristic settle
    time.sleep(0.3)
    if token:
        s.headers.update({"Authorization": f"Bearer {token}"})
    return s

def ers_login_from_file(credentials_path: str = "credentials.json") -> requests.Session:
    """
    Read credentials.json and perform ERS login.

    Args:
        credentials_path (str): Path to credentials JSON file.

    Returns:
        requests.Session: Authenticated session.

    Note:
        credentials.json schema::

            {
              "username": "...",
              "password": "...",
              "token": null
            }
    """
    if not os.path.exists(credentials_path):
        raise AuthError(f"Credentials file not found: {credentials_path}")
    with open(credentials_path, "r") as f:
        creds: Credentials = json.load(f)
    username = creds.get("username") or os.environ.get("USGS_USER")
    password = creds.get("password") or os.environ.get("USGS_PASS")
    token = creds.get("token")

    if not username or not password:
        raise AuthError("ERS username or password not provided")

    return ers_login(username, password, token=token)

def save_cookies_for_gdal(session: requests.Session, cookiefile: str = "usgs_cookies.txt") -> str:
    """
    Save current session cookies into a Mozilla cookie file.

    Args:
        session (requests.Session): Authenticated session.
        cookiefile (str): Path to save cookie file.

    Returns:
        str: Absolute path to saved cookie file.

    Note:
        Use with GDAL via environment variables::

            CPL_CURL_COOKIEFILE=cookiefile
            CPL_CURL_COOKIEJAR=cookiefile
    """
    cj = MozillaCookieJar(cookiefile)
    # Populate from the session's cookie jar
    for c in session.cookies:
        # requests cookie to cookielib cookie (min fields)
        cj.set_cookie(
            requests.cookies.create_cookie(
                name=c.name, value=c.value, domain=c.domain or "landsatlook.usgs.gov",
                path=c.path or "/", secure=c.secure
            )
        )
    cj.save(ignore_discard=True, ignore_expires=True)
    return os.path.abspath(cookiefile)
