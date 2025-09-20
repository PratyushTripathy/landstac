# landstac/types.py
"""
Shared types and aliases for landstac.

This module centralizes light-weight typing helpers to keep function signatures
readable throughout the codebase.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, TypedDict, Optional

# A minimal GeoJSON mapping used for STAC searches and geometry exchange.
GeoJSON = Dict[str, Any]

# Bounding box tuple format: (min_lon, min_lat, max_lon, max_lat)
BBox = Tuple[float, float, float, float]

class Credentials(TypedDict, total=False):
    """
    Container for ERS credentials loaded from a local file or environment.

    Fields
    ------
    username : str
        ERS account username.
    password : str
        ERS account password.
    token : Optional[str]
        Optional bearer token if the host accepts Authorization headers.
        LandsatLook commonly relies on ERS cookies, so this can be null.
    """
    username: str
    password: str
    token: Optional[str]
