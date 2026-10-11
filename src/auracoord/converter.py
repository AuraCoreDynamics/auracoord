"""AuraCoord: Sovereign Military & Geodetic Coordinate Conversion Engine.
Implements Military Spatial Procedures (MSPs) for WGS84:
- Decimal Degrees (DD)
- Degrees Minutes Seconds (DMS)
- Degrees Decimal Minutes (DDM)
- Universal Transverse Mercator (UTM)
- Military Grid Reference System (MGRS)
"""

import math
import re
from typing import Dict, Any, Tuple, Optional

# WGS84 Ellipsoid constants
A = 6378137.0  # semi-major axis (meters)
F = 1.0 / 298.257223563  # flattening
B = A * (1.0 - F)  # semi-minor axis
E_SQ = F * (2.0 - F)  # first eccentricity squared
E_PRIME_SQ = E_SQ / (1.0 - E_SQ)  # second eccentricity squared
K0 = 0.9996  # UTM scale factor

# MGRS 100,000-meter column identification letters
MGRS_EASTING_LETTERS = [
    "ABCDEFGH",  # Set 1 & 4 (UTM zones 1, 7, 13, ...)
    "JKLMNPQR",  # Set 2 & 5 (UTM zones 2, 8, 14, ...)
    "STUVWXYZ",  # Set 3 & 6 (UTM zones 3, 9, 15, ...)
]

# MGRS 100,000-meter row identification letters (even vs odd sets)
MGRS_NORTHING_LETTERS_EVEN = "FGHJKLMNPQRSTUVAB"
MGRS_NORTHING_LETTERS_ODD = "ABCDEFGHJKLMNPQRSTUV"


def latlon_to_dms(lat: float, lon: float) -> str:
    """Convert decimal degrees to Degrees Minutes Seconds (DMS)."""
    lat_hem = "N" if lat >= 0 else "S"
    lat_abs = abs(lat)
    lat_deg = int(lat_abs)
    lat_min_float = (lat_abs - lat_deg) * 60.0
    lat_min = int(lat_min_float)
    lat_sec = (lat_min_float - lat_min) * 60.0

    lon_hem = "E" if lon >= 0 else "W"
    lon_abs = abs(lon)
    lon_deg = int(lon_abs)
    lon_min_float = (lon_abs - lon_deg) * 60.0
    lon_min = int(lon_min_float)
    lon_sec = (lon_min_float - lon_min) * 60.0

    return f"{lat_deg:02d}°{lat_min:02d}'{lat_sec:04.1f}\"{lat_hem} {lon_deg:03d}°{lon_min:02d}'{lon_sec:04.1f}\"{lon_hem}"


def latlon_to_ddm(lat: float, lon: float) -> str:
    """Convert decimal degrees to Degrees Decimal Minutes (DDM)."""
    lat_hem = "N" if lat >= 0 else "S"
    lat_abs = abs(lat)
    lat_deg = int(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60.0

    lon_hem = "E" if lon >= 0 else "W"
    lon_abs = abs(lon)
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60.0

    return f"{lat_deg:02d}°{lat_min:06.3f}'{lat_hem} {lon_deg:03d}°{lon_min:06.3f}'{lon_hem}"


def latlon_to_utm(lat: float, lon: float) -> Tuple[int, str, float, float]:
    """Convert lat/lon to UTM (Zone, Hemisphere, Easting, Northing)."""
    if lon == 180.0:
        lon = -180.0

    zone = int((lon + 180.0) / 6.0) + 1
    hemisphere = "N" if lat >= 0 else "S"

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    central_lon_rad = math.radians((zone - 1) * 6 - 180 + 3)

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    tan_lat = math.tan(lat_rad)

    n = A / math.sqrt(1.0 - E_SQ * sin_lat * sin_lat)
    t = tan_lat * tan_lat
    c = E_PRIME_SQ * cos_lat * cos_lat
    a_diff = cos_lat * (lon_rad - central_lon_rad)

    # Meridian arc length
    m = A * (
        (1.0 - E_SQ / 4.0 - 3.0 * E_SQ * E_SQ / 64.0 - 5.0 * E_SQ * E_SQ * E_SQ / 256.0) * lat_rad
        - (3.0 * E_SQ / 8.0 + 3.0 * E_SQ * E_SQ / 32.0 + 45.0 * E_SQ * E_SQ * E_SQ / 1024.0) * math.sin(2.0 * lat_rad)
        + (15.0 * E_SQ * E_SQ / 256.0 + 45.0 * E_SQ * E_SQ * E_SQ / 1024.0) * math.sin(4.0 * lat_rad)
        - (35.0 * E_SQ * E_SQ * E_SQ / 3072.0) * math.sin(6.0 * lat_rad)
    )

    easting = K0 * n * (
        a_diff
        + (1.0 - t + c) * (a_diff ** 3) / 6.0
        + (5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * E_PRIME_SQ) * (a_diff ** 5) / 120.0
    ) + 500000.0

    northing = K0 * (
        m
        + n * tan_lat * (
            (a_diff ** 2) / 2.0
            + (5.0 - t + 9.0 * c + 4.0 * c * c) * (a_diff ** 4) / 24.0
            + (61.0 - 58.0 * t + t * t + 600.0 * c - 330.0 * E_PRIME_SQ) * (a_diff ** 6) / 720.0
        )
    )

    if lat < 0:
        northing += 10000000.0

    return zone, hemisphere, easting, northing


def get_mgrs_latitude_band(lat: float) -> str:
    """Return UTM MGRS latitude band letter (C to X, omitting I and O)."""
    bands = "CDEFGHJKLMNPQRSTUVWX"
    if lat < -80.0 or lat > 84.0:
        return "Z"
    idx = int((lat + 80.0) / 8.0)
    if idx >= len(bands):
        idx = len(bands) - 1
    return bands[idx]


def latlon_to_mgrs(lat: float, lon: float, precision: int = 5) -> str:
    """Convert Lat/Lon to standard MGRS grid reference."""
    zone, _, easting, northing = latlon_to_utm(lat, lon)
    band = get_mgrs_latitude_band(lat)

    # 100km square column letter
    set_col_idx = (zone - 1) % 3
    col_idx = int(easting / 100000.0) - 1
    col_letter = MGRS_EASTING_LETTERS[set_col_idx][col_idx % 8]

    # 100km square row letter
    is_even_set = ((zone - 1) % 2) == 1
    row_set = MGRS_NORTHING_LETTERS_EVEN if is_even_set else MGRS_NORTHING_LETTERS_ODD
    row_idx = int((northing % 2000000.0) / 100000.0)
    row_letter = row_set[row_idx % len(row_set)]

    # Truncate easting and northing to precision digits
    rem_e = int(easting % 100000.0)
    rem_n = int(northing % 100000.0)

    e_str = f"{rem_e:05d}"[:precision]
    n_str = f"{rem_n:05d}"[:precision]

    return f"{zone:02d}{band}{col_letter}{row_letter}{e_str}{n_str}"


def parse_any_coordinate(text: str) -> Optional[Dict[str, Any]]:
    """Parse coordinate text from DD, DMS, or MGRS into normalized format."""
    if not text:
        return None

    clean = text.strip()

    # 1. Decimal Degrees: e.g. "38.8895, -77.0353" or "38.8895 -77.0353"
    dd_match = re.match(r"^([+-]?\d+(?:\.\d+)?)[,\s]+([+-]?\d+(?:\.\d+)?)$", clean)
    if dd_match:
        lat = float(dd_match.group(1))
        lon = float(dd_match.group(2))
        return format_result(lat, lon, "DecimalDegrees")

    # 2. DMS: e.g. 38°53'22.2"N 77°02'07.1"W
    dms_match = re.match(
        r"(\d+)°(\d+)'([\d.]+)\"([NSns])[,\s]+(\d+)°(\d+)'([\d.]+)\"([EWew])", clean
    )
    if dms_match:
        lat = int(dms_match.group(1)) + int(dms_match.group(2)) / 60.0 + float(dms_match.group(3)) / 3600.0
        if dms_match.group(4).upper() == "S":
            lat = -lat
        lon = int(dms_match.group(5)) + int(dms_match.group(6)) / 60.0 + float(dms_match.group(7)) / 3600.0
        if dms_match.group(8).upper() == "W":
            lon = -lon
        return format_result(lat, lon, "DegreesMinutesSeconds")

    # 3. MGRS: e.g. "18SUJ2345067890" or "18S UJ 23450 67890"
    mgrs_clean = re.sub(r"\s+", "", clean.upper())
    mgrs_match = re.match(r"^(\d{1,2})([C-X])([A-Z]{2})(\d{2,10})$", mgrs_clean)
    if mgrs_match:
        zone = int(mgrs_match.group(1))
        band = mgrs_match.group(2)
        sq = mgrs_match.group(3)
        digits = mgrs_match.group(4)
        half = len(digits) // 2
        e_val = int(digits[:half].ljust(5, "0"))
        n_val = int(digits[half:].ljust(5, "0"))

        # Approximate reverse to lat/lon for camera jump
        lon = (zone - 1) * 6.0 - 180.0 + 3.0
        lat_band_idx = "CDEFGHJKLMNPQRSTUVWX".find(band)
        lat = -80.0 + lat_band_idx * 8.0 + 4.0
        return format_result(lat, lon, "MGRS", original_mgrs=clean)

    return None


def format_result(lat: float, lon: float, detected_format: str, original_mgrs: Optional[str] = None) -> Dict[str, Any]:
    """Compile comprehensive geodetic bundle."""
    zone, hem, easting, northing = latlon_to_utm(lat, lon)
    mgrs = original_mgrs or latlon_to_mgrs(lat, lon)

    return {
        "success": True,
        "detectedFormat": detected_format,
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "dms": latlon_to_dms(lat, lon),
        "ddm": latlon_to_ddm(lat, lon),
        "mgrs": mgrs,
        "utm": f"{zone}{hem} {int(easting)}E {int(northing)}N",
        "utmZone": zone,
        "utmHemisphere": hem,
        "utmEasting": round(easting, 2),
        "utmNorthing": round(northing, 2)
    }
