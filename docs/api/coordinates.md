# Coordinate Conversion

deckgl-dash includes a `CoordinateConverter` utility for converting click coordinates between common geographic formats:

- **DD** — Decimal Degrees (native from deck.gl)
- **DMS** — Degrees Minutes Seconds
- **UTM** — Universal Transverse Mercator
- **MGRS** — Military Grid Reference System

```python
from deckgl_dash import CoordinateConverter
```

---

## CoordinateConverter

Convert geographic coordinates between formats. Works directly with `clickInfo` from DeckGL callbacks.

### From a Click Event

```python
from dash import callback, Output, Input
from deckgl_dash import CoordinateConverter

@callback(Output('coords', 'children'), Input('map', 'clickInfo'))
def show_coords(click_info):
    if not click_info or not click_info.get('coordinate'):
        return "Click on the map..."
    coord = CoordinateConverter.from_click_info(click_info)
    return f"DD: {coord.dd} | DMS: {coord.dms}"
```

### Direct Construction

```python
coord = CoordinateConverter(longitude=-122.4194, latitude=37.7749)
```

### Properties

| Property | Type | Dependencies | Description |
|----------|------|--------------|-------------|
| `.longitude` | `float` | — | Raw longitude value |
| `.latitude` | `float` | — | Raw latitude value |
| `.dd` | `str` | — | Decimal Degrees: `"37.774900 N, 122.419400 W"` |
| `.dd_tuple` | `tuple[float, float]` | — | Raw `(latitude, longitude)` tuple |
| `.dms` | `str` | — | Degrees Minutes Seconds: `"37° 46' 29.64" N, 122° 25' 9.84" W"` |
| `.utm` | `str` | `pyproj` | UTM: `"10S 551234 4182345"` |
| `.mgrs` | `str` | `mgrs` | MGRS with 1m precision: `"10SEG5123482345"` |

### Methods

| Method | Description |
|--------|-------------|
| `CoordinateConverter(longitude, latitude)` | Create from decimal degree values |
| `.from_click_info(click_info)` | Create from a DeckGL `clickInfo` callback dict |
| `.dms_precision(n)` | DMS with `n` decimal places on seconds |
| `.mgrs_precision(n)` | MGRS with `n`-digit precision (1=10km, 2=1km, 3=100m, 4=10m, 5=1m) |
| `.as_dict(include_utm, include_mgrs)` | All formats as a dict. UTM/MGRS included only when flags are `True` |

### Examples

```python
coord = CoordinateConverter(-122.4194, 37.7749)

coord.dd          # '37.774900 N, 122.419400 W'
coord.dd_tuple    # (37.7749, -122.4194)
coord.dms         # '37° 46\' 29.64" N, 122° 25\' 9.84" W'
coord.utm         # '10S 551234 4182345'       (requires pyproj)
coord.mgrs        # '10SEG5123482345'           (requires mgrs)

# Configurable precision
coord.dms_precision(4)    # 4 decimal places on seconds
coord.mgrs_precision(3)   # 100m precision: '10SEG512823'

# All formats at once
coord.as_dict(include_utm=True, include_mgrs=True)
# {
#     'longitude': -122.4194,
#     'latitude': 37.7749,
#     'dd': '37.774900 N, 122.419400 W',
#     'dd_tuple': (37.7749, -122.4194),
#     'dms': '37° 46\' 29.64" N, 122° 25\' 9.84" W',
#     'utm': '10S 551234 4182345',
#     'mgrs': '10SEG5123482345',
# }
```

---

## Optional Dependencies

DD and DMS formats work with no extra dependencies. UTM and MGRS require optional packages:

```bash
# Install both
pip install deckgl-dash[coordinates]

# Or individually
pip install pyproj   # for UTM
pip install mgrs     # for MGRS
```

If you call `.utm` or `.mgrs` without the required package, you'll get a clear `ImportError` with install instructions.

---

## clickInfo Coordinate Data

Clicking anywhere on the map returns coordinate data in `clickInfo`, whether or not a feature was picked:

```python
# clickInfo when clicking empty map space:
{
    'picked': False,
    'coordinate': [-122.4194, 37.7749],
    'x': 450,
    'y': 300,
    'pixel': [450, 300],
    'object': None,
    'properties': None,
}

# clickInfo when clicking a feature:
{
    'picked': True,
    'coordinate': [-122.4194, 37.7749],
    'layerId': 'my-layer',
    'index': 42,
    'object': {...},
    'properties': {...},
}
```

!!! note "Enable click events"
    You must enable click events on the DeckGL component to receive `clickInfo`:
    ```python
    DeckGL(id='map', enable_events=['click'], ...)
    ```
