"""AuraCoord: Sovereign Geodetic and Military Coordinate Conversion Package."""

__version__ = "1.0.1"

from .converter import (
    latlon_to_dms,
    latlon_to_ddm,
    latlon_to_utm,
    latlon_to_mgrs,
    parse_any_coordinate,
)

__all__ = [
    "latlon_to_dms",
    "latlon_to_ddm",
    "latlon_to_utm",
    "latlon_to_mgrs",
    "parse_any_coordinate",
]
