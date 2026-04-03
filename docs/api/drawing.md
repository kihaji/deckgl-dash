# Drawing & Editing

Interactive drawing and editing of geometries on the map. Draw polygons, lines, circles, rectangles, squares, and points, then read the results as GeoJSON in Dash callbacks.

```python
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION
```

## Quick Example

```python
from dash import Dash, html, Input, Output
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

app.layout = html.Div([
    DeckGL(
        id='map',
        layers=[TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png')],
        drawing_config=DrawingConfig(
            mode='draw_polygon',
            style=DrawingStyle(fill_color=[255, 140, 0, 100], line_color='#333333', line_width=2),
        ),
        drawing_features=EMPTY_FEATURE_COLLECTION,
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        style={'height': '600px'},
    ),
    html.Pre(id='output'),
])

@app.callback(Output('output', 'children'), Input('map', 'drawingFeatures'))
def show_features(fc):
    if not fc or not fc.get('features'):
        return "No features drawn yet."
    import json
    return json.dumps(fc, indent=2)
```

---

## DeckGL Drawing Props

These props are added to the `DeckGL` component when drawing is enabled:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `drawing_config` | `DrawingConfig \| dict` | `None` | Drawing mode and style configuration. When set with an active mode, an editable layer appears on top of all other layers |
| `drawing_features` | `dict` | `None` | (Input/Output) GeoJSON FeatureCollection of drawn features. Set from Python to pre-populate or clear; updated from JS when features are added or modified |
| `drawing_event` | `dict` | — | (Output) Information about the last drawing event. Contains `type`, `featureCount`, `timestamp` |

---

## DrawingConfig

Controls which drawing mode is active and how features are styled.

```python
from deckgl_dash import DrawingConfig, DrawingStyle

config = DrawingConfig(
    mode='draw_polygon',
    style=DrawingStyle(fill_color='#FF8C00', line_width=2),
)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `str` | `'view'` | Drawing mode (see [Drawing Modes](#drawing-modes)) |
| `selected_feature_indexes` | `list[int]` | `[]` | Feature indexes selected for editing (for `modify`/`translate` modes) |
| `style` | `DrawingStyle` | `None` | Style overrides for the drawing layer |
| `delete_selected` | `bool` | `False` | Set to `True` to delete the currently selected feature(s). Automatically resets to `False` |

Call `.to_dict()` to serialize for Dash, or pass the object directly to `drawing_config` (auto-serialized).

---

## Drawing Modes

| Mode | String | Interaction |
|------|--------|-------------|
| Polygon | `'draw_polygon'` | Click vertices, double-click to close |
| Line | `'draw_line'` | Click vertices, double-click to finish |
| Circle | `'draw_circle'` | Click center, drag to set radius |
| Rectangle | `'draw_rectangle'` | Click corner, drag to opposite corner |
| Square | `'draw_square'` | Click corner, drag (aspect-ratio constrained) |
| Point | `'draw_point'` | Single click to place |
| Modify | `'modify'` | Click a feature to select, then drag vertices to reshape |
| Translate | `'translate'` | Click a feature to select, then drag to move |
| View | `'view'` | No drawing — normal map interaction |

!!! note "Cursor and map interaction"
    The cursor automatically changes to a crosshair in drawing modes and a pointer in modify/translate modes. Double-click zoom is disabled in all active modes to prevent accidental zooming when finishing a polygon or line. Drag panning is disabled during drag-draw modes (circle, rectangle, square) so the drag gesture draws the shape instead of panning the map.

---

## DrawingStyle

Controls the visual appearance of drawn and in-progress features.

```python
from deckgl_dash import DrawingStyle

style = DrawingStyle(
    fill_color=[255, 140, 0, 100],
    line_color='#333333',
    line_width=2,
    tentative_fill_color=[255, 140, 0, 50],
    tentative_line_color='#FF8C00',
    point_radius=8,
    show_measurements=False,
)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `fill_color` | `color` | `[255, 140, 0, 100]` | Fill color for completed features |
| `line_color` | `color` | `[0, 0, 0, 255]` | Stroke color for completed features |
| `line_width` | `float` | `2` | Stroke width in pixels |
| `tentative_fill_color` | `color` | `[255, 140, 0, 50]` | Fill color for features while being drawn |
| `tentative_line_color` | `color` | `[255, 140, 0, 200]` | Stroke color for features while being drawn |
| `edit_handle_point_color` | `color` | `[255, 0, 0, 255]` | Color of vertex edit handles in modify mode |
| `point_radius` | `float` | `5` | Radius of drawn points in pixels |
| `show_measurements` | `bool` | `True` | Show distance/area tooltips while drawing lines and circles |

Colors accept hex strings (`'#FF8C00'`), RGB tuples (`(255, 140, 0)`), or RGBA lists (`[255, 140, 0, 100]`).

---

## Switching Modes

Use a Dash callback to switch between drawing modes:

```python
from dash import Dash, html, Input, Output, callback_context, no_update
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION

MODE_MAP = {
    'btn-polygon': 'draw_polygon',
    'btn-line': 'draw_line',
    'btn-circle': 'draw_circle',
    'btn-rectangle': 'draw_rectangle',
    'btn-modify': 'modify',
}

@app.callback(
    Output('map', 'drawingConfig'),
    [Input(btn_id, 'n_clicks') for btn_id in MODE_MAP],
    prevent_initial_call=True,
)
def switch_mode(*_):
    btn = str(callback_context.triggered_id)
    mode = MODE_MAP.get(btn, 'view')
    return DrawingConfig(mode=mode, style=my_style).to_dict()
```

---

## Deleting Features

### Delete Selected

In `modify` or `translate` mode, click a feature to select it, then trigger deletion:

```python
from dash import State

@app.callback(
    Output('map', 'drawingConfig'),
    Input('btn-delete', 'n_clicks'),
    State('map', 'drawingConfig'),
    prevent_initial_call=True,
)
def delete_selected(n, current_config):
    # Set deleteSelected flag on the current config
    return {**(current_config or {}), 'deleteSelected': True}
```

The component deletes the selected feature(s), syncs the updated `drawingFeatures` to Python, and automatically resets `deleteSelected` to `False`.

### Clear All

To remove all drawn features, set `drawingFeatures` to an empty FeatureCollection:

```python
from deckgl_dash import EMPTY_FEATURE_COLLECTION

@app.callback(
    Output('map', 'drawingFeatures'),
    Input('btn-clear', 'n_clicks'),
    prevent_initial_call=True,
)
def clear_all(n):
    return EMPTY_FEATURE_COLLECTION
```

---

## Reading Drawn Features

Drawn features are synced to Python as a GeoJSON FeatureCollection via the `drawingFeatures` prop whenever a feature is completed:

```python
@app.callback(
    Output('output', 'children'),
    Input('map', 'drawingFeatures'),
)
def on_features(fc):
    if not fc or not fc.get('features'):
        return "No features."
    # fc is a standard GeoJSON FeatureCollection
    # Each feature has geometry (Polygon, LineString, Point) and properties
    return f"{len(fc['features'])} features drawn"
```

The `drawingEvent` prop provides metadata about the last edit:

| Key | Type | Description |
|-----|------|-------------|
| `type` | `str` | Event type: `'addFeature'`, `'finishMovePosition'`, `'deleteFeature'`, etc. |
| `featureCount` | `int` | Number of features after the edit |
| `timestamp` | `int` | Unix timestamp in milliseconds |

---

## Pre-populating Features

Set `drawing_features` to a GeoJSON FeatureCollection in the layout to start with existing features:

```python
existing = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-122.4, 37.8], [-122.4, 37.7], [-122.3, 37.7], [-122.3, 37.8], [-122.4, 37.8]]],
            },
            "properties": {},
        }
    ],
}

DeckGL(
    id='map',
    drawing_config=DrawingConfig(mode='modify'),
    drawing_features=existing,
    ...
)
```

---

## JSON Dict Alternative

`DrawingConfig` and `DrawingStyle` are convenience helpers. You can also pass raw dicts:

```python
DeckGL(
    id='map',
    drawing_config={
        'mode': 'draw_polygon',
        'style': {
            'fillColor': [255, 140, 0, 100],
            'lineColor': [51, 51, 51, 255],
            'lineWidth': 2,
            'showMeasurements': False,
        },
    },
    drawing_features={'type': 'FeatureCollection', 'features': []},
    ...
)
```

!!! note "camelCase in dicts"
    When using raw dicts, style keys use camelCase (`fillColor`, `lineWidth`, `showMeasurements`) matching the JavaScript property names. The Python helpers accept `snake_case` and convert automatically.
