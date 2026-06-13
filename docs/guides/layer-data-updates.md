# Layer Data Updates

## The Problem

When you update the `layers` prop, **every** layer's configuration and data is serialized and sent from Python to the browser — even layers that haven't changed. For apps with many layers or large datasets, this creates unnecessary overhead.

## The Solution: `layer_data`

The `layer_data` prop lets you update individual layer data by ID without touching the rest of the layer stack:

- **`layers`** = defines the layer stack (types, styling, structure). Full rebuild when changed.
- **`layer_data`** = per-layer data overrides, merged on top of `layers` by matching layer IDs.

## Basic Pattern

Define your layers once in the layout (with empty data placeholders if needed), then update specific layers via callbacks:

```python
from dash import Dash, html, callback, Output, Input
from deckgl_dash import DeckGL
from deckgl_dash.layers import HexagonLayer, ScatterplotLayer, process_layers

app = Dash(__name__)

app.layout = html.Div([
    html.Button("Load", id="btn-load"),
    html.Button("Clear", id="btn-clear"),
    DeckGL(
        id='map',
        layers=process_layers([
            HexagonLayer(id='hexagons', data=[], get_position='@@=coordinates', radius=100),
            ScatterplotLayer(id='scatter', data=STATIC_POINTS, get_position='@@=coordinates'),
        ]),
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
    ),
])


@callback(Output('map', 'layerData'), Input('btn-load', 'n_clicks'), prevent_initial_call=True)
def load_data(n):
    return {'hexagons': generate_points()}  # only hexagon data is sent
```

The ScatterplotLayer data is never re-serialized — only the `hexagons` key is sent over the wire.

## Using Dash `Patch()` for Independent Updates

When multiple callbacks independently update different layers, use `Patch()` to avoid conflicts:

```python
from dash import callback, Output, Input, Patch

@callback(Output('map', 'layerData'), Input('toggle-layer-a', 'value'), prevent_initial_call=True)
def update_layer_a(value):
    patched = Patch()
    patched['layer-a'] = load_data_a() if value else []
    return patched


@callback(Output('map', 'layerData'), Input('toggle-layer-b', 'value'), prevent_initial_call=True)
def update_layer_b(value):
    patched = Patch()
    patched['layer-b'] = load_data_b() if value else []
    return patched
```

Each callback only sends its own layer's data. Dash merges the patches on the client.

!!! note "Duplicate Output with Patch()"
    Multiple callbacks can target `Output('map', 'layerData')` when using `Patch()`, because each callback modifies different keys in the dict. This is a standard Dash pattern for dict-valued props.

## When to Use `layers` vs `layer_data`

| Scenario | Use |
|----------|-----|
| Adding/removing layers from the stack | `layers` |
| Changing layer styling (colors, opacity, radius) | `layers` |
| Changing layer type | `layers` |
| Updating a layer's data | `layer_data` |
| Loading data after initial render | `layer_data` |
| Independent per-layer data updates | `layer_data` + `Patch()` |
| Changing the rendering order | `layer_order` (see [Layer Ordering](layer-ordering.md)) |

## Click-to-Highlight (accessor recolor)

A common interaction is highlighting a feature when its name is clicked in a list (or
when the feature itself is clicked on the map). The robust pattern is **accessor-based
recolor**: store a `selected` flag in each feature's `properties` and color via a ternary
accessor, then push the updated data through `layer_data`. This works reliably across
composite layers (`GeoJsonLayer`, `PolygonLayer`) where `highlightedObjectIndex` does not.

```python
from dash import callback, Output, Input, ctx, ALL
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer

# Selected feature -> yellow, otherwise its own color. The @@= expression binder
# exposes `properties`, so selectable fields must live under properties.*
HIGHLIGHT = "@@=properties.selected ? [255, 255, 0, 200] : properties.color"

def build_fc(selected_name=None):
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature',
         'properties': {'name': r['name'], 'color': r['color'], 'selected': r['name'] == selected_name},
         'geometry': {'type': 'Polygon', 'coordinates': [r['polygon']]}}
        for r in REGIONS
    ]}

DeckGL(
    id='map',
    layers=[GeoJsonLayer(id='regions', data=build_fc(), get_fill_color=HIGHLIGHT, pickable=True)],
    enable_events=['click'],
    ...
)

@callback(
    Output('map', 'layerData'),
    Input({'type': 'name-btn', 'index': ALL}, 'n_clicks'),
    Input('map', 'clickInfo'),
    prevent_initial_call=True,
)
def highlight(_btn_clicks, click_info):
    trig = ctx.triggered_id
    if isinstance(trig, dict):                       # a list button was clicked
        name = REGIONS[trig['index']]['name']
    elif click_info and click_info.get('picked'):    # a feature on the map was clicked
        name = (click_info.get('properties') or {}).get('name')
    else:
        name = None                                  # clicked empty map -> clear
    return {'regions': build_fc(name)}               # only this layer's data is re-sent
```

Because the same accessor form (`properties.selected ? ... : properties.color`) works for
paths too (store the fields under a `properties` key on each path record), one callback can
highlight polygons and paths together — see `examples/feature_list_highlight_demo.py`.

## Migration from `dcc.Store` + Full Rebuild

If you previously used `dcc.Store` to hold layer data and rebuilt the entire `layers` array on every change:

=== "Before (full rebuild)"

    ```python
    dcc.Store(id='hexagon-data', data=[]),

    DeckGL(id='map', layers=process_layers([...]))

    @callback(Output('hexagon-data', 'data'), Input('btn', 'n_clicks'))
    def load(n):
        return generate_points()

    @callback(Output('map', 'layers'), Input('hexagon-data', 'data'))
    def rebuild(data):
        return process_layers([
            HexagonLayer(id='hexagons', data=data, ...),
            ScatterplotLayer(id='scatter', data=STATIC_POINTS, ...),  # re-sent every time!
        ])
    ```

=== "After (targeted update)"

    ```python
    DeckGL(
        id='map',
        layers=process_layers([
            HexagonLayer(id='hexagons', data=[], ...),
            ScatterplotLayer(id='scatter', data=STATIC_POINTS, ...),
        ]),
    )

    @callback(Output('map', 'layerData'), Input('btn', 'n_clicks'))
    def load(n):
        return {'hexagons': generate_points()}  # only hexagon data sent
    ```

## Behavioral Notes

- Keys in `layer_data` that don't match any layer ID in `layers` are silently ignored.
- When `layer_data` is `None` or empty, there is zero overhead — the fast path creates layers directly from `layers`.
- Changing `layers` triggers a full layer rebuild. The current `layer_data` is re-merged on top of the new layer configs.
