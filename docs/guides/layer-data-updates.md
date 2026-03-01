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
