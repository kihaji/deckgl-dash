# deckgl-dash

[![PyPI](https://img.shields.io/pypi/v/deckgl-dash)](https://pypi.org/project/deckgl-dash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Direct deck.gl wrapper for Plotly Dash - high-performance WebGL-powered visualization.

## Installation

```bash
pip install deckgl-dash
```

## Quick Start

```python
from dash import Dash, html
from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, GeoJsonLayer

app = Dash(__name__)

app.layout = DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True)
    ],
    initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
)

if __name__ == '__main__':
    app.run(debug=True)
```

## Features

- **High Performance**: WebGL-powered rendering for 1M+ data points at 60fps
- **Full deck.gl Support**: All deck.gl layer types via JSON configuration
- **Python Helpers**: Ergonomic layer constructors (`GeoJsonLayer`, `TileLayer`, etc.)
- **MapLibre GL JS Basemaps**: Vector tile basemaps with automatic view state synchronization
- **Tile-based Maps**: TileLayer support for OSM, CARTO, and custom tile servers
- **Track Visualization**: Per-segment path coloring and direction-of-travel arrows for pattern-of-life / track analysis (`multi_color`, `show_direction`)
- **Time Slider & Animation**: GPU-filtered sliding time window with 60fps client-side playback and zero per-frame server round trips (`time_filter` prop, `get_filter_value` accessor)
- **Fit to Bounds**: Viewport-aware `fit_bounds` prop + `compute_bounds` helper to tightly frame features
- **Per-Layer Data Updates**: Update individual layer data without resending all layers via `layer_data` prop
- **Remote Data Loading**: Load data directly from external servers in the browser with `load_options`, including client certificate (mTLS) support
- **Data-driven Styling**: Built-in color scales powered by chroma.js

## MapLibre GL JS Integration

Use MapLibre GL JS as the basemap renderer with deck.gl layers as overlays. This gives you access to vector tile basemaps (CARTO, OpenFreeMap, MapTiler) with full styling control.

### Basic Basemap

```python
from dash import Dash
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer, ScatterplotLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

app = Dash(__name__)

app.layout = DeckGL(
    id='map',
    maplibre_config=MapLibreConfig(
        style=MapLibreStyle.CARTO_POSITRON,
    ).to_dict(),
    layers=[
        GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF5722', pickable=True),
    ],
    initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
)
```

### Available Styles

| Constant | Provider |
|----------|----------|
| `MapLibreStyle.CARTO_POSITRON` | CARTO (light) |
| `MapLibreStyle.CARTO_DARK_MATTER` | CARTO (dark) |
| `MapLibreStyle.CARTO_VOYAGER` | CARTO (colorful) |
| `MapLibreStyle.OPENFREEMAP_LIBERTY` | OpenFreeMap |
| `MapLibreStyle.OPENFREEMAP_BRIGHT` | OpenFreeMap |
| `MapLibreStyle.OPENFREEMAP_POSITRON` | OpenFreeMap |

MapTiler styles are also available (`MAPTILER_STREETS`, `MAPTILER_SATELLITE`, etc.) but require an API key appended to the URL.

### Custom Raster Sources

Add custom raster tile sources (XYZ, WMS) to the MapLibre basemap:

```python
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle, RasterSource, RasterLayer

config = MapLibreConfig(
    style=MapLibreStyle.empty(),  # Empty style for raster-only maps
    sources={
        'custom-tiles': RasterSource(
            tiles=['https://tiles.example.com/{z}/{x}/{y}.png'],
            tile_size=256,
        ),
    },
    map_layers=[
        RasterLayer(id='raster-layer', source='custom-tiles'),
    ],
)
```

### Vector Tile Styling

Add custom vector tile sources and style them with MapLibre layers:

```python
from deckgl_dash.maplibre import MapLibreConfig, VectorSource, FillLayer, LineLayer

config = MapLibreConfig(
    style='https://tiles.openfreemap.org/styles/liberty',
    sources={
        'custom': VectorSource(tiles=['https://example.com/{z}/{x}/{y}.pbf']),
    },
    map_layers=[
        FillLayer(
            id='buildings',
            source='custom',
            source_layer='buildings',
            fill_color='#ff0000',
            fill_opacity=0.5,
        ),
        LineLayer(
            id='roads',
            source='custom',
            source_layer='roads',
            line_color='#000000',
            line_width=2,
        ),
    ],
)
```

### MapLibre Layer Types

| Class | MapLibre Type | Use Case |
|-------|---------------|----------|
| `FillLayer` | `fill` | Filled polygons |
| `LineLayer` | `line` | Lines and polygon outlines |
| `RasterLayer` | `raster` | Raster tile display |
| `CircleLayer` | `circle` | Points as circles |
| `SymbolLayer` | `symbol` | Text labels and icons |
| `FillExtrusionLayer` | `fill-extrusion` | 3D extruded polygons |

### Interleaved Mode

By default, deck.gl layers render on top of all MapLibre layers for best performance. Set `interleaved=True` to render deck.gl layers between MapLibre layers (e.g., below labels), at the cost of reduced pan/zoom performance:

```python
config = MapLibreConfig(
    style=MapLibreStyle.CARTO_POSITRON,
    interleaved=True,  # Allows deck.gl layers below MapLibre labels
)
```

## Path Tracks: Per-Segment Color & Direction

For pattern-of-life / track analysis, `PathLayer` can color each **segment** independently
and overlay **direction-of-travel arrows** — all on a single, pickable layer.

```python
from deckgl_dash.layers import PathLayer

# Each record carries its path plus one color per segment (N points -> N-1 segments).
track = [{
    'path': [[-122.42, 37.77], [-122.41, 37.77], [-122.36, 37.80], [-122.35, 37.80]],
    'segmentColors': [[30, 110, 230], [230, 30, 30], [30, 110, 230]],  # middle leg flagged red
}]

PathLayer(
    id='track',
    data=track,
    get_path='@@=path',
    get_color='@@=segmentColors',
    multi_color=True,        # color each segment from the list above
    show_direction=True,     # evenly-spaced arrows pointing in the travel direction
    arrow_spacing=80,        # pixels between arrows (stays constant across zoom)
    get_width=6,
    width_min_pixels=4,
    pickable=True,
)
```

- `multi_color=True` → serializes to `MultiColorPathLayer`; `get_color` returns one color per segment.
- `show_direction=True` → serializes to `DirectedPathLayer`, a composite that draws the line **and** arrows as one object. Arrows are spaced in screen pixels and inherit the segment color (override with `arrow_color`).

See `examples/multicolor_path_demo.py` and `examples/directed_path_demo.py`.

## Time Slider & Animation

Filter visible data to a **sliding time window** and animate it across the full time range.
Filtering runs entirely **on the GPU** (deck.gl's `DataFilterExtension`) and playback is
driven by an internal `requestAnimationFrame` loop, so the map updates at **60fps with no
per-frame round trips** to the Dash server — the data is shipped to the browser once. Only
the throttled `current_time` is reported back, so a `dcc.Slider` handle and readouts can
track playback and other callbacks can react.

Give any filterable layer a `get_filter_value` accessor (a per-datum timestamp) and pass a
`time_filter` config built with `build_time_filter`:

```python
from dash import Dash, dcc, html, callback, Output, Input, State, ctx, no_update
from deckgl_dash import DeckGL, compute_time_domain, build_time_filter
from deckgl_dash.layers import TileLayer, ScatterplotLayer

# Each point carries a numeric time `t` (keep it float32-safe — see note below).
DOMAIN = compute_time_domain(POINTS, 't')          # [t_min, t_max]
WINDOW = (DOMAIN[1] - DOMAIN[0]) * 0.1             # show a 10%-wide trailing window

app.layout = html.Div([
    dcc.Slider(id='time', min=DOMAIN[0], max=DOMAIN[1], value=DOMAIN[0] + WINDOW, updatemode='drag'),
    DeckGL(
        id='map',
        layers=[
            TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
            ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates',
                             get_filter_value='@@=t'),  # auto-attaches DataFilterExtension
        ],
        time_filter=build_time_filter(DOMAIN, WINDOW),  # playing=False by default
    ),
])

# The engine reports current_time (~8 Hz) during playback; use it to move the slider handle.
@callback(Output('time', 'value'), Input('map', 'currentTime'), prevent_initial_call=True)
def track(t):
    return t
```

Set `playing=True` (e.g. from a Play button writing the `time_filter` prop) to animate; the
window slides as `current - window … current` advances. Direction-of-travel arrows
(`show_direction=True`) filter together with their lines.

**`time_filter` fields** (build with `build_time_filter(domain, window, ...)`):

| Key | Description |
|-----|-------------|
| `domain` | `[t_min, t_max]` full time extent (use `compute_time_domain`) |
| `window` | Sliding-window width; visible data is `[current - window, current]` |
| `current` | Head time `T`; authoritative while paused (slider scrubbing) |
| `playing` | Run the animation loop |
| `speed` | Time units advanced per wall-clock second (default: full sweep in ~20s) |
| `loop` | Wrap the head back to `domain[0] + window` at the end |
| `soft_edge` | Optional fade width mapped to `filterSoftRange` |
| `layer_ids` | Explicit target layer IDs (default: auto-detect filterable layers) |

> **Float32 note:** `DataFilterExtension` uploads filter values as 32-bit floats, so raw
> epoch seconds (~1.7e9) lose precision and the window jumps. Keep time values float32-safe
> (e.g. seconds/days since the domain start), or attach the extension with `fp64=True`.

`get_filter_value` is supported directly on `ScatterplotLayer`, `GeoJsonLayer`, and
`PathLayer` (incl. `show_direction`/`multi_color`), and on any other layer via `**kwargs`.
See `examples/time_slider_demo.py` and the
[API docs](docs/api/deckgl-component.md#time-filtering-and-animation).

## Fit to Bounds

Frame the camera to a bounding box with the viewport-aware `fit_bounds` prop. It uses the
map's real container size (MapLibre's native `fitBounds`, or `WebMercatorViewport` in
deck-only mode), so features are framed tightly instead of approximately. Build the box from
your features with `compute_bounds` (accepts points, paths, polygons, or GeoJSON):

```python
from deckgl_dash import DeckGL, compute_bounds
from deckgl_dash.layers import ScatterplotLayer

DeckGL(
    id='map',
    layers=[ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates')],
    initial_view_state={'longitude': -100, 'latitude': 40, 'zoom': 3},
    fit_bounds={'bounds': compute_bounds(POINTS), 'padding': 40, 'maxZoom': 16},
)
```

`fit_bounds` is `{'bounds': [[west, south], [east, north]], 'padding': 20, 'maxZoom': 20}`.
See the [API docs](docs/api/deckgl-component.md#fit-to-bounds) and `examples/zoom_to_fit_demo.py`.

## Color Scales (chroma.js)

deckgl-dash includes powerful data-driven color mapping using chroma.js scales:

```python
from deckgl_dash import ColorScale, color_range_from_scale
from deckgl_dash.layers import GeoJsonLayer, HexagonLayer

# Fluent API for data-driven fill colors
scale = ColorScale('viridis').domain(0, 100).alpha(180)
layer = GeoJsonLayer(
    id='choropleth',
    data=geojson,
    get_fill_color=scale.accessor('properties.value'),  # @@scale(viridis, properties.value, 0, 100, 180)
    pickable=True
)

# Available scale modifiers
ColorScale('plasma').reverse()      # Reverse color direction
ColorScale('OrRd').log()            # Logarithmic scaling
ColorScale('Spectral').sqrt()       # Square root scaling

# Generate color arrays for aggregation layers
color_range = color_range_from_scale('viridis', 6)  # [[68,1,84], [59,82,139], ...]
hexagon_layer = HexagonLayer(
    id='hexagons',
    data=points,
    color_range=color_range,
    ...
)
```

### Available Color Scales

**Sequential**: `OrRd`, `PuBu`, `BuPu`, `Oranges`, `BuGn`, `YlOrBr`, `YlGn`, `Reds`, `RdPu`, `Greens`, `YlGnBu`, `Purples`, `GnBu`, `Greys`, `YlOrRd`, `PuRd`, `Blues`, `PuBuGn`

**Diverging**: `Spectral`, `RdYlGn`, `RdBu`, `PiYG`, `PRGn`, `RdYlBu`, `BrBG`, `RdGy`, `PuOr`

**Perceptually Uniform**: `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `turbo`

## Remote Data Loading

Layers can fetch data directly from an external server in the browser, bypassing the Dash server. This supports client certificate authentication (mTLS) where the browser presents certificates from the OS/browser store.

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

The `load_options` prop is available on all layer types. Use `enable_events=['dataLoad', 'dataLoadError']` to receive Dash callbacks via `data_load_info` and `data_load_error` output props when remote data loads or fails.

See the [API docs](docs/api/deckgl-component.md#remote-data-loading) for full details on CORS requirements and mTLS configuration.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Development Setup

1. Install npm packages
    ```bash
    npm install
    ```

2. Create a virtual env and activate
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # or: .venv\Scripts\activate  # Windows
    ```

3. Install python packages
    ```bash
    pip install -r requirements.txt
    ```

4. Build the component
    ```bash
    npm run build
    ```

5. Run the example
    ```bash
    python usage.py
    ```

### Releasing a New Version

1. Bump the version in `pyproject.toml`
2. Build the production JS bundle:
    ```bash
    make build
    ```
3. Commit the version bump and built JS
4. Create a release tag (requires clean git tree):
    ```bash
    make release VERSION=x.y.z
    ```
5. Push to trigger the PyPI publish workflow:
    ```bash
    git push && git push --tags
    ```

## License

MIT License - see [LICENSE](./LICENSE)
