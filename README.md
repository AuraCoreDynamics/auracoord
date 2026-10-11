# AuraCoord 🌐📐

**Sovereign Geodetic & Military Coordinate Conversion Engine**  
*Pure-Python Military Spatial Procedures (MSPs) for WGS84, MGRS, UTM, DMS, DDM, and Decimal Degrees.*

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://python.org)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Stdlib)-brightgreen.svg)](#pure-python-architecture)
[![Standards](https://img.shields.io/badge/Standard-WGS84%20%2F%20NATO%20MGRS-darkgreen.svg)](#supported-coordinate-systems)

---

## Overview

**AuraCoord** is an open-source, zero-dependency geodetic calculation package engineered for sovereign geospatial platforms, tactical mission workstations, and air-gapped environments.

Traditional GIS coordinate conversion stacks depend on heavy C/C++ native bindings (e.g., GDAL/PROJ) which can be brittle to cross-compile, deploy on hardened operating systems, or embed into edge microservices. AuraCoord implements rigorous mathematical geodetic transforms directly in pure Python using only standard library modules, guaranteeing 100% portability, instantaneous installation, and microsecond conversion performance.

### Capabilities
- **Bidirectional Conversions**: Instantly transforms between Decimal Degrees (DD), Degrees Minutes Seconds (DMS), Degrees Decimal Minutes (DDM), Universal Transverse Mercator (UTM), and Military Grid Reference System (MGRS).
- **Tactical String Parsing**: Robust regex-assisted heuristic parser that identifies and decodes messy user inputs, military grids, and legacy GPS notations.
- **Standalone Tkinter Desktop GUI**: Native, zero-dependency tactical coordinate converter window with live two-way updates and single-click copy buttons.
- **Embedded REST Microservice**: Lightweight HTTP server (`/api/coord/convert`, `/api/coord/search`, `/api/coord/parse`) for external web clients such as **AuraMist**.
- **AuraRouter Integration**: Published `aurarouter.manifest.json` enabling semantic location resolution across the sovereign network mesh.

---

## Supported Coordinate Systems

| Coordinate System | Format Specifier | Typical Example | Notes |
|:---|:---|:---|:---|
| **Decimal Degrees (DD)** | `lat, lon` | `38.889444, -77.035278` | Standard digital and web mapping format (EPSG:4326). |
| **Degrees Minutes Seconds (DMS)** | `DD°MM'SS.S"H` | `38°53'22.0"N 077°02'07.0"W` | Standard nautical, aviation, and field navigation format. |
| **Degrees Decimal Minutes (DDM)** | `DD°MM.MMM'H` | `38°53.367'N 077°02.117'W` | Standard maritime GPS and search-and-rescue (SAR) notation. |
| **Universal Transverse Mercator (UTM)** | `Zone[H] Easting Northing` | `18N 323456 4305882` | Transverse Mercator conformal projection; metric coordinates. |
| **Military Grid Reference System (MGRS)** | `GZD + 100km ID + Digits` | `18SUJ2345605882` | NATO standard tactical grid referencing (1m to 10km precision). |

---

## Pure-Python Architecture & Mathematics

AuraCoord performs high-precision ellipsoidal trigonometry based on the **WGS84** reference ellipsoid:
- **Semi-major axis ($a$)**: $6,378,137.0\text{ m}$
- **Flattening ($f$)**: $1 / 298.257223563$
- **UTM Scale Factor ($k_0$)**: $0.9996$
- **False Easting**: $500,000.0\text{ m}$
- **False Northing (Southern Hemisphere)**: $10,000,000.0\text{ m}$

### Algorithms
- **Transverse Mercator Forward Projection**: Uses fifth-order meridian arc length expansions and Taylor series for latitude-longitude to conformal Easting/Northing transformation.
- **Transverse Mercator Reverse Projection**: Footpoint latitude iterations with second-eccentricity series expansions.
- **MGRS Lettering Engine**: Dynamic 100,000-meter square column letters (`A`–`Z` excluding `I` and `O`) across 6-zone repeating sets, and row progression alternating between even and odd UTM zones.

---

## Installation

### From Source (Editable Mode)
```bash
git clone https://github.com/AuraCoreDynamics/auracoord.git
cd auracoord
pip install -e .
```

### Zero Dependencies
AuraCoord does not require NumPy, SciPy, PROJ, or GDAL. It runs on stock Python 3.10+ environments.

---

## Usage

### 1. Standalone Desktop GUI
Launch the tactical coordinate converter desktop application:
```bash
python -m auracoord.gui
```
*(Or run `auracoord` if installed on your PATH).*

**Features**:
- Input any format into the Tactical Input box or any of the 5 individual fields.
- Real-time two-way synchronization: modifying any field immediately updates all other 4 fields.
- Single-click clipboard copy buttons for rapid radio or tactical transmission.

### 2. Standalone REST Microservice
Launch the lightweight HTTP microservice:
```bash
python -m auracoord.server
```
*(Or run `auracoord-server` if installed on your PATH).*

By default, listens on `http://0.0.0.0:7087`.

#### Endpoints:
- `GET /health`: Health status and supported standards.
- `GET /api/coord/convert?lat=38.889444&lon=-77.035278`: Returns all 5 representations.
- `GET /api/coord/search?q=18SUJ2345605882`: Decodes any coordinate string.
- `POST /api/coord/parse`: Post JSON `{"text": "38°53'22.0\"N 077°02'07.0\"W"}`.

**Example Response**:
```json
{
  "status": "success",
  "matched_type": "MGRS",
  "lat": 38.889444,
  "lon": -77.035278,
  "dd": "38.889444, -77.035278",
  "dms": "38°53'22.0\"N 077°02'07.0\"W",
  "ddm": "38°53.367'N 077°02.117'W",
  "utm": "18N 323456 4305882",
  "mgrs": "18SUJ2345605882"
}
```

### 3. Python Programmatic API
```python
from auracoord.converter import (
    latlon_to_dms,
    latlon_to_ddm,
    latlon_to_utm,
    latlon_to_mgrs,
    parse_any_coordinate,
    format_result
)

# Convert lat/lon to MGRS
mgrs_str = latlon_to_mgrs(38.889444, -77.035278)
print(mgrs_str)  # 18SUJ2345605882

# Parse an unknown coordinate string
result = parse_any_coordinate("18SUJ2345605882")
print(result["lat"], result["lon"])  # 38.889444, -77.035278
print(result["dms"])  # 38°53'22.0"N 077°02'07.0"W
```

---

## Integration with AuraMist

In **AuraMist**, AuraCoord powers the coordinate jump bar and tactical HUD overlay:

```typescript
// Query AuraCoord microservice for tactical coordinate jump
async function jumpToCoordinate(query: string) {
  const resp = await fetch(`http://tactical-node.auracore.internal:7087/api/coord/search?q=${encodeURIComponent(query)}`);
  if (!resp.ok) throw new Error("Invalid coordinate");
  const data = await resp.json();
  
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(data.lon, data.lat, 15000.0)
  });
}
```

---

## Running Automated Tests

Run the standard Python unit test suite:
```powershell
python -m unittest discover -s tests
```

Tests cover:
- Mathematical forward and reverse UTM projections.
- MGRS string generation across Northern and Southern hemisphere zones.
- Latitude-longitude to DMS / DDM transformations with sub-second precision.
- Free-form text parser resilience against varying delimiters, whitespace, and case.

---

## License

This project is licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE) file for complete terms and copyright details.
