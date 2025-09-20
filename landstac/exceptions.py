# landstac/exceptions.py
"""
Package-specific exceptions for landstac.

These exceptions make it easier to catch and handle common failure modes
such as authentication issues, STAC search errors, and download problems.
"""

class AuthError(RuntimeError):
    """Authentication failed or session is not authorized for the requested resource."""


class DownloadError(RuntimeError):
    """Download failed or the remote server returned an error."""


class StacError(RuntimeError):
    """STAC query failed or returned unexpected results."""
