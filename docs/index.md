# deckgl-dash

[![PyPI](https://img.shields.io/pypi/v/deckgl-dash)](https://pypi.org/project/deckgl-dash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Direct deck.gl wrapper for Plotly Dash** — high-performance WebGL-powered visualization for large vector datasets, tile-based maps, and data-driven styling.

---

## Key Features

- **High Performance** — WebGL-powered rendering for 1M+ data points at 60fps
- **Full deck.gl Support** — All deck.gl layer types via JSON configuration
- **Python Helpers** — Ergonomic layer constructors (`GeoJsonLayer`, `TileLayer`, etc.)
- **MapLibre GL JS Basemaps** — Vector tile basemaps with automatic view state sync
- **Tile-based Maps** — TileLayer support for OSM, CARTO, and custom tile servers
- **Data-driven Styling** — Built-in color scales powered by chroma.js

## Quick Install

```bash
pip install deckgl-dash
```

## Minimal Example

```python
from dash import Dash
from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, GeoJsonLayer

app = Dash(__name__)

app.layout = DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True),
    ],
    initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
)

if __name__ == '__main__':
    app.run(debug=True)
```

## Next Steps

<div class="grid cards" markdown>

- :material-download: **[Installation](getting-started/installation.md)** — Install and verify the package
- :material-rocket-launch: **[Quick Start](getting-started/quick-start.md)** — Build your first map in minutes
- :material-map: **[MapLibre Integration](guides/maplibre-integration.md)** — Vector tile basemaps and styling
- :material-book-open-variant: **[API Reference](api/deckgl-component.md)** — Full component and layer docs

</div>
