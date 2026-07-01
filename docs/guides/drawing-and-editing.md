# Drawing & Editing Geometries

This guide walks through common patterns for adding interactive drawing to your Dash app.

## Basic Setup

Every drawing-enabled map needs three things:

1. **`drawing_config`** — which mode is active and how features look
2. **`drawing_features`** — the GeoJSON FeatureCollection (input/output)
3. **A callback** — to read or react to drawn features

```python
from dash import Dash, html, Input, Output
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

app.layout = html.Div([
    DeckGL(
        id='map',
        layers=[TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png')],
        drawing_config=DrawingConfig(mode='draw_polygon'),
        drawing_features=EMPTY_FEATURE_COLLECTION,
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        style={'height': '600px'},
    ),
    html.Div(id='status'),
])

@app.callback(Output('status', 'children'), Input('map', 'drawingFeatures'))
def on_draw(fc):
    if not fc:
        return ""
    return f"{len(fc['features'])} feature(s) drawn"
```

## Building a Drawing Toolbar

A common pattern is a row of buttons that each activate a different drawing mode:

```python
from dash import Dash, html, Input, Output, callback_context, no_update
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

STYLE = DrawingStyle(
    fill_color=[255, 140, 0, 100],
    line_color='#333333',
    line_width=2,
    tentative_fill_color=[255, 140, 0, 50],
    tentative_line_color='#FF8C00',
)

MODE_MAP = {
    'btn-polygon': 'draw_polygon',
    'btn-line': 'draw_line',
    'btn-circle': 'draw_circle',
    'btn-rectangle': 'draw_rectangle',
    'btn-point': 'draw_point',
    'btn-modify': 'modify',
    'btn-delete': 'delete',
}

app.layout = html.Div([
    html.Div([
        html.Button("Polygon", id="btn-polygon"),
        html.Button("Line", id="btn-line"),
        html.Button("Circle", id="btn-circle"),
        html.Button("Rectangle", id="btn-rectangle"),
        html.Button("Point", id="btn-point"),
        html.Button("Modify", id="btn-modify"),
        html.Button("Delete", id="btn-delete"),
        html.Button("Clear All", id="btn-clear"),
    ]),
    DeckGL(
        id='map',
        layers=[TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png')],
        drawing_config=DrawingConfig(mode='draw_polygon', style=STYLE),
        drawing_features=EMPTY_FEATURE_COLLECTION,
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        style={'height': '600px'},
    ),
])


@app.callback(
    Output('map', 'drawingConfig'),
    Output('map', 'drawingFeatures'),
    [Input(btn_id, 'n_clicks') for btn_id in [*MODE_MAP.keys(), 'btn-clear']],
    prevent_initial_call=True,
)
def toolbar_action(*args):
    btn = str(callback_context.triggered_id)
    if btn == 'btn-clear':
        return DrawingConfig(mode='view', style=STYLE).to_dict(), EMPTY_FEATURE_COLLECTION
    mode = MODE_MAP.get(btn, 'view')
    return DrawingConfig(mode=mode, style=STYLE).to_dict(), no_update
```

## Editing Existing Features

### Modify Mode

Switch to `modify` mode to reshape existing features. Click a feature to select it, then drag its vertices:

```python
DrawingConfig(mode='modify', style=STYLE)
```

Selected features are highlighted with a distinct color. Edit handles (red dots by default) appear at each vertex.

### Translate Mode

Switch to `translate` mode to move entire features. Click a feature to select it, then drag to reposition:

```python
DrawingConfig(mode='translate', style=STYLE)
```

### Delete Mode

Switch to `delete` mode to remove features one by one — each click on a feature deletes it immediately, no prior selection needed:

```python
DrawingConfig(mode='delete', style=STYLE)
```

### Deleting the Selected Feature Programmatically

Alternatively, while in `modify` or `translate` mode you can delete the currently selected feature by setting `deleteSelected: True` on the current config:

```python
@app.callback(
    Output('map', 'drawingConfig'),
    Input('btn-delete', 'n_clicks'),
    State('map', 'drawingConfig'),
    prevent_initial_call=True,
)
def delete_selected(n, config):
    return {**(config or {}), 'deleteSelected': True}
```

The flag resets automatically after the deletion.

## Customizing Appearance

### Style Properties

```python
style = DrawingStyle(
    fill_color=[255, 140, 0, 100],           # completed feature fill
    line_color='#333333',                     # completed feature stroke
    line_width=3,                             # stroke width (pixels)
    tentative_fill_color=[255, 140, 0, 50],   # fill while drawing
    tentative_line_color='#FF8C00',           # stroke while drawing
    edit_handle_point_color=[255, 0, 0, 255], # vertex handles in modify mode
    point_radius=10,                          # radius of drawn points (pixels)
    show_measurements=False,                  # hide distance/area tooltips
)
```

### Hiding Measurement Tooltips

Lines and circles show distance/area tooltips by default while drawing. To disable them:

```python
DrawingStyle(show_measurements=False)
```

### Point Size

Control the radius of drawn point features:

```python
DrawingStyle(point_radius=15)  # larger points (default is 5)
```

## Data Flow

The drawing system uses a dual-state approach for responsiveness:

1. **JavaScript state** — updated on every user interaction (vertex placement, drag) for immediate visual feedback
2. **Python state** — synced via `drawingFeatures` only when a feature is completed or an edit finishes

This means the map feels responsive during drawing, while Python callbacks only fire on meaningful events (not every mouse move).

### Event Types

The `drawingEvent` output prop tells you what happened:

| Event Type | When |
|-----------|------|
| `addFeature` | A new feature was completed |
| `finishMovePosition` | A vertex or feature was moved (modify/translate) |
| `deleteFeature` | A feature was deleted (via `delete` mode or `deleteSelected`) |
| `addPosition` | A vertex was added during drawing |
| `removePosition` | A vertex was removed during editing |

## Combining with Other Layers

The drawing layer always renders on top of all other layers. You can combine it with any existing layer stack:

```python
DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='existing-data', data=geojson, get_fill_color='#4488FF', pickable=True),
    ],
    drawing_config=DrawingConfig(mode='draw_polygon', style=STYLE),
    drawing_features=EMPTY_FEATURE_COLLECTION,
    enable_events=['click'],  # click events still work for non-drawing layers
    ...
)
```

!!! tip "Drawing layer ID"
    The drawing layer uses the internal ID `__drawing-layer`. It does not appear in `layers` and cannot be targeted by `layer_data` or `layer_order`.
