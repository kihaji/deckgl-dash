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
- **Per-Layer Data Updates**: Update individual layer data without resending all layers via `layer_data` prop
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

## License

MIT License - see [LICENSE](./LICENSE)
