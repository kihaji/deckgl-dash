# DeckGL Component

The `DeckGL` component is the main Dash component for rendering deck.gl maps.

```python
from deckgl_dash import DeckGL
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | Component ID for Dash callbacks |
| `layers` | `list[dict]` | `[]` | Array of deck.gl layer configurations. Each layer needs a `@@type` property (or use Python helper classes) |
| `layer_data` | `dict[str, Any]` | `None` | Per-layer data overrides. Dict mapping layer IDs to data values. See [Updating Layer Data](#updating-layer-data) |
| `initial_view_state` | `dict` | `{longitude: -122.4, latitude: 37.8, zoom: 11, pitch: 0, bearing: 0}` | Initial camera position (uncontrolled mode) |
| `view_state` | `dict` | — | Controlled view state — when set, fully controls the camera |
| `controller` | `bool \| dict` | `True` | Enable map interactions. `True` for all, `False` for none, or a dict for fine-grained control |
| `enable_events` | `bool \| list[str]` | `False` | Enable events for callbacks. `False`, `True` (all), or list like `['click', 'hover', 'dataLoadError']` |
| `tooltip` | `bool \| dict` | `False` | Tooltip on hover. `True` for default, or `{html: "template {property}", style: {}}` |
| `style` | `dict` | — | CSS style dict for the container element |
| `maplibre_config` | `dict` | — | MapLibre GL JS configuration (see [MapLibre API](maplibre.md)) |

!!! warning "controller is ignored in MapLibre mode"
    When `maplibre_config` is provided, the `controller` prop has no effect. Use `map_options` in `MapLibreConfig` instead. See the [MapLibre Integration Guide](../guides/maplibre-integration.md#controller-gotcha).

## Output Props

These props are updated by the component and can be read in Dash callbacks:

| Prop | Type | Description |
|------|------|-------------|
| `click_info` | `dict` | Information about the last click on the map. Includes geographic coordinates whether or not a feature was picked. See [Coordinate Conversion](coordinates.md) |
| `hover_info` | `dict` | Information about the currently hovered feature |
| `map_style_loaded` | `bool` | `True` when the MapLibre style has finished loading |
| `data_load_info` | `dict` | Information about the last successful remote data load. Contains `layerId`, `featureCount`, `timestamp` |
| `data_load_error` | `dict` | Information about the last data load error. Contains `layerId`, `error`, `timestamp` |

## View State

The `initial_view_state` dict accepts:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `longitude` | `float` | `-122.4` | Longitude of the map center |
| `latitude` | `float` | `37.8` | Latitude of the map center |
| `zoom` | `float` | `11` | Zoom level (0 = world, ~20 = building) |
| `pitch` | `float` | `0` | Tilt angle in degrees (0 = top-down, 60 = angled) |
| `bearing` | `float` | `0` | Rotation in degrees (0 = north up) |

## Enabling Events

Events are disabled by default for performance:

```python
# Enable all events
DeckGL(id='map', enable_events=True, ...)

# Enable specific events only
DeckGL(id='map', enable_events=['click', 'hover'], ...)

# Enable data loading events (for remote URL layers)
DeckGL(id='map', enable_events=['dataLoad', 'dataLoadError'], ...)

# No events (default)
DeckGL(id='map', enable_events=False, ...)
```

Available event types: `'click'`, `'hover'`, `'viewStateChange'`, `'dataLoad'`, `'dataLoadError'`.

## Tooltip Configuration

```python
# Show all feature properties
DeckGL(id='map', tooltip=True, ...)

# Custom HTML template
DeckGL(
    id='map',
    tooltip={
        'html': '<b>{name}</b><br/>Population: {population}',
        'style': {'backgroundColor': 'steelblue', 'color': 'white'},
    },
    ...
)
```

## Using Layers

Layers can be provided as Python helper objects or raw JSON dicts:

=== "Python Helpers"

    ```python
    from deckgl_dash.layers import GeoJsonLayer, TileLayer

    DeckGL(
        id='map',
        layers=[
            TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
            GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True),
        ],
        ...
    )
    ```

=== "JSON Dicts"

    ```python
    DeckGL(
        id='map',
        layers=[
            {'@@type': 'TileLayer', 'id': 'basemap', 'data': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'},
            {'@@type': 'GeoJsonLayer', 'id': 'data', 'data': geojson, 'getFillColor': [255, 140, 0], 'pickable': True},
        ],
        ...
    )
    ```

Python helpers automatically convert `snake_case` props to `camelCase` and normalize hex color strings to `[r, g, b]` arrays.

## Updating Layer Data

The `layer_data` prop lets you update individual layer data without resending the entire `layers` array. Define your layer stack once in the layout, then target specific layers by ID:

```python
from dash import callback, Output, Input
from deckgl_dash import DeckGL
from deckgl_dash.layers import HexagonLayer, ScatterplotLayer, process_layers

# Layout: define layers once (data can be empty placeholders)
DeckGL(
    id='map',
    layers=process_layers([
        HexagonLayer(id='hexagons', data=[], get_position='@@=coordinates', radius=100),
        ScatterplotLayer(id='scatter', data=STATIC_POINTS, get_position='@@=coordinates'),
    ]),
    ...
)

# Callback: update only the hexagon layer's data
@callback(Output('map', 'layerData'), Input('load-btn', 'n_clicks'))
def load_data(n):
    return {'hexagons': generate_points()}  # only this payload is serialized
```

- `layers` = source of truth for layer structure and styling. Full rebuild when changed.
- `layer_data` = per-layer data overrides, merged on top of `layers` by matching layer IDs.
- Keys in `layer_data` that don't match any layer ID are silently ignored.
- Dash `Patch()` works naturally since `layer_data` is a dict prop.

See the [Layer Data Updates Guide](../guides/layer-data-updates.md) for detailed patterns.

## Remote Data Loading

Layers can load data directly from a remote URL in the browser, bypassing the Dash server. This is useful when the data is served by an external server, or when the browser needs to present client certificates (mTLS) that the server-side application does not have access to.

Pass a URL string as the `data` prop and use `load_options` to configure the fetch request:

```python
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer, TileLayer

DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(
            id='remote-data',
            data='https://secure-server.com/api/features.geojson',
            load_options={
                'fetch': {
                    'credentials': 'include',  # send cookies and client certificates
                    'mode': 'cors',
                    'headers': {'X-Custom-Header': 'value'},
                }
            },
            get_fill_color='#FF8C00',
            pickable=True,
        ),
    ],
    initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
    enable_events=['dataLoadError'],  # opt-in to error callbacks
)
```

### `load_options`

The `load_options` dict is passed through to deck.gl's loaders.gl. The most common sub-key is `fetch`, which accepts all standard [fetch API `RequestInit`](https://developer.mozilla.org/en-US/docs/Web/API/Request/Request#options) options:

| Key | Type | Description |
|-----|------|-------------|
| `credentials` | `str` | `'include'` to send cookies/certs cross-origin, `'same-origin'` (default), or `'omit'` |
| `mode` | `str` | `'cors'` (default for cross-origin), `'same-origin'`, or `'no-cors'` |
| `headers` | `dict` | Custom HTTP headers to send with the request |
| `cache` | `str` | Cache mode: `'default'`, `'no-cache'`, `'reload'`, `'force-cache'`, `'only-if-cached'` |

`load_options` is available on all layer types: GeoJsonLayer, ScatterplotLayer, PathLayer, LineLayer, ArcLayer, IconLayer, TextLayer, PolygonLayer, TileLayer, MVTLayer, and BitmapLayer. Other layers can pass it via `**kwargs`.

### Client Certificate Authentication (mTLS)

When the remote server requires a client certificate, set `credentials: 'include'` in `load_options`. The browser will present certificates from the OS/browser certificate store during the TLS handshake. No JavaScript code is needed to select the certificate -- the browser handles this automatically based on its configuration.

!!! note "CORS requirements"
    The remote server must return appropriate CORS headers. For credentialed requests (`credentials: 'include'`), the server **must** set `Access-Control-Allow-Credentials: true` and **cannot** use `Access-Control-Allow-Origin: *` -- it must specify the exact requesting origin.

### Data Load Events

To receive callbacks when remote data loads or fails, add `'dataLoad'` and/or `'dataLoadError'` to `enable_events`:

```python
from dash import Dash, callback, Output, Input, html
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer

app = Dash(__name__)

app.layout = html.Div([
    DeckGL(
        id='map',
        layers=[
            GeoJsonLayer(
                id='remote-data',
                data='https://example.com/data.geojson',
                load_options={'fetch': {'credentials': 'include'}},
                get_fill_color='#FF8C00',
            ),
        ],
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        enable_events=['dataLoad', 'dataLoadError'],
    ),
    html.Div(id='status'),
])

@callback(Output('status', 'children'), Input('map', 'data_load_info'))
def on_data_loaded(info):
    if info is None:
        return 'Loading...'
    return f"Loaded {info['featureCount']} features from layer '{info['layerId']}'"

@callback(Output('status', 'children', allow_duplicate=True),
          Input('map', 'data_load_error'), prevent_initial_call=True)
def on_data_error(error):
    if error is None:
        return ''
    return f"Error loading layer '{error['layerId']}': {error['error']}"
```
