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
- **Tile-based Maps**: TileLayer support for OSM, CARTO, and custom tile servers
- **Data-driven Styling**: Built-in color scales powered by chroma.js

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
