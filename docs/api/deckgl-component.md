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
| `layer_order` | `list[str]` | `None` | Layer rendering order as a list of layer IDs from bottom to top. See [Layer Ordering](#layer-ordering) |
| `initial_view_state` | `dict` | `{longitude: -122.4, latitude: 37.8, zoom: 11, pitch: 0, bearing: 0}` | Initial camera position (uncontrolled mode) |
| `view_state` | `dict` | — | Controlled view state — when set, fully controls the camera |
| `fit_bounds` | `dict` | — | Fit the camera to a geographic bounding box. See [Fit to Bounds](#fit-to-bounds) |
| `controller` | `bool \| dict` | `True` | Enable map interactions. `True` for all, `False` for none, or a dict for fine-grained control |
| `enable_events` | `bool \| list[str]` | `False` | Enable events for callbacks. `False`, `True` (all), or list like `['click', 'hover', 'dataLoadError']` |
| `tooltip` | `bool \| dict` | `False` | Tooltip on hover. `True` for default, or `{html: "template {property}", style: {}}` |
| `style` | `dict` | — | CSS style dict for the container element |
| `maplibre_config` | `dict` | — | MapLibre GL JS configuration (see [MapLibre API](maplibre.md)) |
| `drawing_config` | `DrawingConfig \| dict` | `None` | Drawing/editing configuration (see [Drawing & Editing](drawing.md)) |
| `drawing_features` | `dict` | `None` | (Input/Output) GeoJSON FeatureCollection of drawn features |
| `time_filter` | `dict` | `None` | Sliding-window time filter + animation config. See [Time Filtering and Animation](#time-filtering-and-animation) |

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
| `drawing_event` | `dict` | Information about the last drawing event. Contains `type`, `featureCount`, `timestamp`. See [Drawing & Editing](drawing.md) |
| `current_time` | `float` | The current playback head time during a `time_filter` animation, reported ~8 Hz. See [Time Filtering and Animation](#time-filtering-and-animation) |

## View State

The `initial_view_state` dict accepts:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `longitude` | `float` | `-122.4` | Longitude of the map center |
| `latitude` | `float` | `37.8` | Latitude of the map center |
| `zoom` | `float` | `11` | Zoom level (0 = world, ~20 = building) |
| `pitch` | `float` | `0` | Tilt angle in degrees (0 = top-down, 60 = angled) |
| `bearing` | `float` | `0` | Rotation in degrees (0 = north up) |

## Fit to Bounds

Set the `fit_bounds` prop to frame the camera to a geographic bounding box. Unlike a
hand-computed zoom, this is **viewport-aware** — it uses the map container's real pixel
size, so features are framed tightly. It works in both render modes (MapLibre's native
`fitBounds`, or `WebMercatorViewport.fitBounds` in deck-only mode).

`fit_bounds` is a dict:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `bounds` | `[[west, south], [east, north]]` | — | **Required.** The box to fit |
| `padding` | `float` | `20` | Pixels of padding around the bounds |
| `maxZoom` | `float` | `20` | Clamp the fitted zoom (used as the fallback for a single-point box) |

Use the `compute_bounds` helper to derive `bounds` from your features — it accepts point
lists, path/polygon dicts, or GeoJSON:

```python
from dash import callback, Output, Input
from deckgl_dash import DeckGL, compute_bounds
from deckgl_dash.layers import ScatterplotLayer

DeckGL(
    id='map',
    layers=[ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates')],
    initial_view_state={'longitude': -100, 'latitude': 40, 'zoom': 3},  # starts zoomed out
    fit_bounds={'bounds': compute_bounds(POINTS), 'padding': 40, 'maxZoom': 16},
)

# Or drive it from a callback:
@callback(Output('map', 'fitBounds'), Input('fit-btn', 'n_clicks'), prevent_initial_call=True)
def zoom_to_fit(n):
    return {'bounds': compute_bounds(POINTS), 'padding': 40}
```

!!! tip "Re-firing on identical bounds"
    Dash skips a prop update when the value is unchanged. If a button always fits the
    same bounds, add a changing key (e.g. `'nonce': n_clicks`) so the update re-fires;
    the component ignores unknown keys.

`compute_bounds(data, *, get_coordinates=None)` returns `[[west, south], [east, north]]`
and raises `ValueError` if no coordinates are found. Pass `get_coordinates` to extract
coordinates from a non-standard key. See `examples/zoom_to_fit_demo.py` (deck-only) and
`examples/all_layers_deferred_visibility_demo.py` (deferred load across all layer types).

## Time Filtering and Animation

The `time_filter` prop restricts the visible data to a **sliding time window**
`[current - window, current]` and can **animate** that window across the full time range.
Filtering runs on the GPU via deck.gl's `DataFilterExtension`, and playback is driven by an
internal `requestAnimationFrame` loop — so the map updates at **60fps with no per-frame
round trips** to the Dash server. The full dataset is shipped to the browser once; during
playback only the throttled `current_time` output is sent back (~8 Hz).

### 1. Give layers a `get_filter_value` accessor

Each filterable layer needs a per-datum numeric time value. Supplying `get_filter_value`
auto-attaches the `DataFilterExtension`:

```python
ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates',
                 get_filter_value='@@=t')  # extensions=['DataFilterExtension'] is auto-added
```

`get_filter_value` is a first-class parameter on `ScatterplotLayer`, `GeoJsonLayer`, and
`PathLayer` (including `show_direction`/`multi_color`), and works on any other layer via
`**kwargs`. Layers without it (e.g. a basemap `TileLayer`) are never filtered.

!!! warning "Keep time values float32-safe"
    `DataFilterExtension` uploads filter values as **32-bit floats** (~16.7M integer
    precision). Raw epoch seconds (~1.7e9) lose precision and the window jumps. Use a
    smaller scale — e.g. **seconds/days since the domain start** — or attach the extension
    explicitly with `fp64=True` (`extensions=[{'@@type': 'DataFilterExtension', 'fp64': True}]`).

### 2. Build and pass `time_filter`

Use `build_time_filter(domain, window, ...)` (and `compute_time_domain` to find the extent):

```python
from deckgl_dash import DeckGL, compute_time_domain, build_time_filter

DOMAIN = compute_time_domain(POINTS, 't')        # [t_min, t_max]
WINDOW = (DOMAIN[1] - DOMAIN[0]) * 0.1

DeckGL(id='map', layers=[...], time_filter=build_time_filter(DOMAIN, WINDOW))
```

The `time_filter` dict accepts:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `domain` | `[t_min, t_max]` | — | **Required for playback.** Full time extent |
| `window` | `float` | — | Sliding-window width; visible data is `[current - window, current]` |
| `current` | `float` | `domain[0] + window` | Head time `T`; authoritative while paused (scrubbing) |
| `playing` | `bool` | `False` | Run the animation loop |
| `speed` | `float` | full sweep in ~20s | Time units advanced per wall-clock second |
| `loop` | `bool` | `True` | Wrap the head back to `domain[0] + window` at the end |
| `soft_edge` | `float` | `None` | Fade width mapped to `filterSoftRange` for fade in/out |
| `layer_ids` | `list[str]` | auto-detect | Explicit target layer IDs (default: any layer with the extension) |
| `nonce` | `int` | `None` | Bump to force a re-sync of an unchanged `current` |

`compute_time_domain(data, accessor)` returns `[t_min, t_max]`; `accessor` may be a dict
key, a dotted path (`'properties.t'`), or a callable. It accepts a list of records or a
GeoJSON FeatureCollection and raises `ValueError` if no numeric values are found.

### 3. Wire the controls

A single callback typically owns `time_filter` (Play/Pause/speed buttons + scrubbing) plus
the slider handle and a readout. During playback the engine pushes `current_time`; echo it
to the slider's `value` to make the handle track playback, and **ignore slider input while
`playing`** so the echo doesn't fight the animation:

```python
@callback(
    Output('map', 'timeFilter'), Output('time-slider', 'value'), Output('readout', 'children'),
    Input('btn-play', 'n_clicks'), Input('btn-pause', 'n_clicks'),
    Input('time-slider', 'value'), Input('map', 'currentTime'),
    State('map', 'timeFilter'), prevent_initial_call=True,
)
def control(_play, _pause, slider_value, current_time, tf):
    tf = dict(tf)
    trig = ctx.triggered_id
    if trig == 'map':                       # playback tick: move handle + readout only
        return no_update, current_time, f't = {current_time:.1f}'
    if trig == 'btn-play':
        tf['playing'] = True; return tf, no_update, no_update
    if trig == 'btn-pause':
        tf['playing'] = False; return tf, no_update, no_update
    if trig == 'time-slider':
        if tf.get('playing'):               # programmatic echo during playback — ignore
            return no_update, no_update, no_update
        tf['current'] = slider_value; tf['nonce'] = (tf.get('nonce') or 0) + 1
        return tf, no_update, f't = {slider_value:.1f}'
    return no_update, no_update, no_update
```

Direction-of-travel arrows (`show_direction=True`) filter together with their lines. See
`examples/time_slider_demo.py` (scatter points) and
`examples/time_slider_demo.py` (time slider) and `examples/directed_path_demo.py` (directed paths).

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

## Layer Ordering

deck.gl renders layers in array order — the first layer in the list is drawn at the bottom, the last is drawn on top. The `layer_order` prop lets you control this rendering order dynamically without resending layer data.

```python
# Layers render in array order by default (basemap bottom, points top)
DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='polygons', data=polygon_data, get_fill_color='#FF8C00'),
        ScatterplotLayer(id='points', data=point_data, get_position='@@=coordinates'),
    ],
)

# Set explicit order (points below polygons)
DeckGL(
    id='map',
    layers=[...],
    layer_order=['basemap', 'points', 'polygons'],
)
```

Reorder dynamically via a Dash callback:

```python
@callback(Output('map', 'layerOrder'), Input('order-dropdown', 'value'))
def reorder(value):
    if value == 'points-on-top':
        return ['basemap', 'polygons', 'points']
    return ['basemap', 'points', 'polygons']
```

- When `layer_order` is `None` or an empty list, layers render in their original array order.
- Layer IDs in `layer_order` that don't match any layer are silently skipped.
- Layers not listed in `layer_order` are appended at the top.
- Works independently of `layer_data` — you can update data and reorder in separate callbacks.

See the [Layer Ordering Guide](../guides/layer-ordering.md) for detailed patterns.

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
