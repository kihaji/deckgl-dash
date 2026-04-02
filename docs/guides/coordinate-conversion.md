# Coordinate Conversion Guide

This guide shows how to click anywhere on a deck.gl map and display the location in multiple coordinate formats.

## Basic Setup

Enable click events on your DeckGL component and use `CoordinateConverter` in a callback:

```python
from dash import Dash, html, callback, Output, Input
from deckgl_dash import DeckGL, CoordinateConverter
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

app.layout = html.Div([
    DeckGL(
        id='map',
        layers=[
            TileLayer(
                id='basemap',
                data='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                min_zoom=0, max_zoom=19,
                tile_size=256,
            ),
        ],
        initial_view_state={'longitude': -98.58, 'latitude': 39.83, 'zoom': 4},
        enable_events=['click'],
        style={'width': '100%', 'height': '600px'},
    ),
    html.Div(id='coord-output', style={'marginTop': '20px', 'fontFamily': 'monospace'}),
])

@callback(Output('coord-output', 'children'), Input('map', 'clickInfo'))
def display_coordinates(click_info):
    if not click_info or not click_info.get('coordinate'):
        return "Click on the map to see coordinates..."
    coord = CoordinateConverter.from_click_info(click_info)
    return [
        html.Div(f"Decimal Degrees:  {coord.dd}"),
        html.Div(f"DMS:              {coord.dms}"),
    ]

if __name__ == '__main__':
    app.run(debug=True)
```

## Adding UTM and MGRS

Install the optional dependencies:

```bash
pip install deckgl-dash[coordinates]
```

Then extend your callback:

```python
@callback(Output('coord-output', 'children'), Input('map', 'clickInfo'))
def display_coordinates(click_info):
    if not click_info or not click_info.get('coordinate'):
        return "Click on the map to see coordinates..."

    coord = CoordinateConverter.from_click_info(click_info)
    return [
        html.Div(f"DD:    {coord.dd}"),
        html.Div(f"DMS:   {coord.dms}"),
        html.Div(f"UTM:   {coord.utm}"),
        html.Div(f"MGRS:  {coord.mgrs}"),
    ]
```

## Handling Optional Dependencies Gracefully

If you're distributing an app where users may or may not have `pyproj`/`mgrs` installed:

```python
coord = CoordinateConverter.from_click_info(click_info)
rows = [
    html.Div(f"DD:   {coord.dd}"),
    html.Div(f"DMS:  {coord.dms}"),
]
try:
    rows.append(html.Div(f"UTM:  {coord.utm}"))
except ImportError:
    rows.append(html.Div("UTM:  (install pyproj)"))
try:
    rows.append(html.Div(f"MGRS: {coord.mgrs}"))
except ImportError:
    rows.append(html.Div("MGRS: (install mgrs)"))
return rows
```

## Combining with Feature Picks

`clickInfo` now includes coordinates whether or not a feature was clicked. You can show both:

```python
@callback(Output('coord-output', 'children'), Input('map', 'clickInfo'))
def display_click(click_info):
    if not click_info or not click_info.get('coordinate'):
        return "Click on the map..."

    coord = CoordinateConverter.from_click_info(click_info)
    rows = [html.Div(f"Location: {coord.dd}")]

    if click_info.get('picked'):
        props = click_info.get('properties', {})
        rows.append(html.Div(f"Feature: {props.get('name', 'unknown')}"))
        rows.append(html.Div(f"Layer: {click_info['layerId']}"))

    return rows
```

## Using as_dict for JSON Output

The `.as_dict()` method returns all formats in a single dict, useful for storing or displaying as JSON:

```python
coord = CoordinateConverter.from_click_info(click_info)
all_formats = coord.as_dict(include_utm=True, include_mgrs=True)
# Returns: {'longitude': ..., 'latitude': ..., 'dd': ..., 'dms': ..., 'utm': ..., 'mgrs': ...}
```

## Format Reference

| Format | Example | Precision | Dependencies |
|--------|---------|-----------|--------------|
| DD | `37.774900 N, 122.419400 W` | 6 decimal places (~0.11m) | None |
| DMS | `37° 46' 29.64" N, 122° 25' 9.84" W` | 2 decimal places on seconds | None |
| UTM | `10S 551234 4182345` | 1 meter | `pyproj` |
| MGRS | `10SEG5123482345` | 1 meter (5-digit) | `mgrs` |
