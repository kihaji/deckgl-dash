# dash-deckgl: Direct deck.gl Wrapper for Plotly Dash

## Overview

Create a custom Dash component that wraps deck.gl directly (without pydeck) for high-performance web mapping with support for large vector datasets, Cloud Optimized GeoTIFFs (COGs), and tile-based base maps.

**Target**: Internal use for your Dash application (not public PyPI release).

## Feasibility Assessment: HIGH

**Key findings from research:**
- Dash custom components are well-documented with React + PropTypes pattern
- deck.gl has excellent performance (1M+ items at 60fps) and a clean React wrapper
- Existing dash-deck/pydeck has significant limitations we can avoid

## Architecture

### Design Philosophy: JSON Core + Optional Python Helpers

1. **JSON/Dict-based core**: Direct deck.gl JSON format for full flexibility
2. **Python helper classes**: Ergonomic layer constructors (no pydeck dependency)

### Base Map Strategy
- **MVP**: Use deck.gl's TileLayer with raster tiles (OSM, CARTO, etc.)
- **Future**: Design allows adding MapLibre GL integration later if vector base maps needed

### Project Structure

```
dash-deckgl/
├── dash_deckgl/
│   ├── __init__.py
│   ├── DeckGL.py                 # Auto-generated Dash component
│   └── layers/                   # Python helper classes
│       ├── __init__.py
│       ├── base.py               # BaseLayer class
│       ├── core.py               # GeoJsonLayer, ScatterplotLayer, etc.
│       ├── geo.py                # TileLayer, MVTLayer
│       ├── aggregation.py        # HeatmapLayer, HexagonLayer, etc.
│       └── raster.py             # COGLayer, BitmapLayer
├── src/lib/
│   ├── components/
│   │   └── DeckGL.react.js       # Main React component
│   └── utils/
│       ├── layerRegistry.js      # Layer type registry (ALL deck.gl layers)
│       └── eventHandler.js       # Event normalization
├── examples/
├── tests/
├── package.json
├── webpack.config.js
└── pyproject.toml
```

## Python API Design

### Option 1: Pure JSON (Power Users)
```python
DeckGL(
    id='map',
    layers=[{
        '@@type': 'GeoJsonLayer',
        'id': 'geojson',
        'data': 'https://example.com/data.geojson',
        'getFillColor': [255, 140, 0],
        'pickable': True
    }],
    initialViewState={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
)
```

### Option 2: Python Helpers (Convenience)
```python
from dash_deckgl.layers import GeoJsonLayer, TileLayer

DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='data', data=geojson, get_fill_color=[255, 140, 0], pickable=True)
    ],
    initialViewState={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
)
```

## Key Component Props

| Prop | Type | Description |
|------|------|-------------|
| `id` | string | Unique component identifier |
| `layers` | list | Array of layer configs (JSON or helper objects) |
| `initialViewState` | dict | Initial camera position (longitude, latitude, zoom, pitch, bearing) |
| `viewState` | dict | Controlled view state (for programmatic control) |
| `controller` | bool/dict | Enable map interactions |
| `enableEvents` | bool/list | Event opt-in: `['click', 'hover']` or `True` for all |
| `tooltip` | bool/dict | Tooltip configuration |
| `style` | dict | CSS styles for container (width, height) |
| `clickInfo` | dict | (Output) Last clicked feature info |
| `hoverInfo` | dict | (Output) Currently hovered feature info |

## Layer Support (Full deck.gl Catalog)

All deck.gl layers will be supported from the start via the layer registry. Python helpers will be created for the most commonly used layers.

### Core Layers (@deck.gl/layers)
| Layer | Python Helper | Description |
|-------|---------------|-------------|
| GeoJsonLayer | Yes | Vector data (polygons, lines, points) |
| ScatterplotLayer | Yes | Large point datasets (millions of points) |
| PathLayer | Yes | Line/path rendering |
| PolygonLayer | Yes | Polygon fills |
| LineLayer | Yes | Simple line segments |
| ArcLayer | Yes | Arcs between points (great for flow maps) |
| IconLayer | Yes | Icons/markers at points |
| TextLayer | Yes | Text labels |
| ColumnLayer | No | 3D columns/cylinders |
| GridCellLayer | No | Grid cells |
| BitmapLayer | Yes | Image overlays |
| PointCloudLayer | No | 3D point clouds |

### Geo Layers (@deck.gl/geo-layers)
| Layer | Python Helper | Description |
|-------|---------------|-------------|
| TileLayer | Yes | XYZ raster tile servers |
| MVTLayer | Yes | Mapbox Vector Tiles |
| TerrainLayer | No | 3D terrain from DEM tiles |
| Tile3DLayer | No | 3D tiles (Cesium format) |
| TripsLayer | No | Animated paths over time |
| H3HexagonLayer | No | H3 hexagonal grid |
| S2Layer | No | S2 geometry cells |
| GreatCircleLayer | No | Great circle arcs |

### Aggregation Layers (@deck.gl/aggregation-layers)
| Layer | Python Helper | Description |
|-------|---------------|-------------|
| HeatmapLayer | Yes | Density heatmaps |
| HexagonLayer | Yes | Hexagonal binning |
| GridLayer | Yes | Square grid binning |
| ScreenGridLayer | No | Screen-space grid |
| ContourLayer | No | Contour lines from points |
| CPUGridLayer | No | CPU-based grid aggregation |

### Custom/Raster Layers
| Layer | Python Helper | Description |
|-------|---------------|-------------|
| COGLayer | Yes | Cloud Optimized GeoTIFFs (custom, uses deck.gl-geotiff) |

**Note**: All layers can be used via JSON/dict format even without Python helpers.

## Performance Optimizations

1. **Events disabled by default** - Opt-in for click/hover to avoid callback overhead
2. **Binary data transport** - Support for TypedArrays to skip JSON serialization
3. **Efficient layer updates** - deck.gl only re-renders changed layers
4. **GPU acceleration** - All rendering on GPU, handles 1M+ points at 60fps

## Implementation Phases

### Phase 1: Project Setup & Core Component
**Goal**: Working Dash component with all deck.gl layers available

1. Initialize project with dash-component-boilerplate
2. Implement DeckGL React component:
   - View state management (controlled + uncontrolled modes)
   - Layer registry with ALL deck.gl layer types
   - Accessor parsing (`@@=property.path` syntax)
   - Event handling (click, hover) with opt-in pattern
   - Tooltip support
3. Build pipeline: webpack + dash-generate-components
4. Basic Python package structure

**Files to create:**
- `src/lib/components/DeckGL.react.js`
- `src/lib/utils/layerRegistry.js`
- `src/lib/utils/eventHandler.js`
- `package.json`, `webpack.config.js`

### Phase 2: Python Layer Helpers
**Goal**: Pythonic API for common layers

1. Create base layer class with `to_dict()` serialization
2. Implement Python helpers for priority layers:
   - Core: GeoJsonLayer, ScatterplotLayer, PathLayer, LineLayer, ArcLayer
   - Geo: TileLayer, MVTLayer, BitmapLayer
   - Aggregation: HeatmapLayer, HexagonLayer, GridLayer
3. Unit tests for layer serialization

**Files to create:**
- `dash_deckgl/layers/base.py`
- `dash_deckgl/layers/core.py`
- `dash_deckgl/layers/geo.py`
- `dash_deckgl/layers/aggregation.py`

### Phase 3: COG/Raster Support
**Goal**: Cloud Optimized GeoTIFF visualization

1. Integrate @developmentseed/deck.gl-geotiff
2. Create COGLayer (custom layer wrapping geotiff loader)
3. Add colormap support (viridis, plasma, inferno, etc.)
4. Example with real COG data

**Files to create:**
- `dash_deckgl/layers/raster.py`
- `src/lib/layers/COGLayer.js` (custom layer)

### Phase 4: Examples & Testing
**Goal**: Verify everything works for your use case

1. Create example applications:
   - Basic GeoJSON visualization
   - Large scatterplot (100k+ points)
   - Tile base map + vector overlay
   - COG raster display
   - Multi-layer with aggregation
2. Integration tests with dash.testing
3. Performance benchmarks

## Key Dependencies

**JavaScript (npm):**
- @deck.gl/core ~9.0 - Core rendering engine
- @deck.gl/layers ~9.0 - Standard layer types
- @deck.gl/geo-layers ~9.0 - Geospatial layers (Tile, MVT, etc.)
- @deck.gl/aggregation-layers ~9.0 - Heatmap, hexagon, grid
- @deck.gl/react ~9.0 - React component wrapper
- @developmentseed/deck.gl-geotiff ~0.3 - COG support

**Python:**
- dash >= 2.0.0

**Optional Python (for advanced use):**
- numpy - Binary data transport for large datasets

**Note**: No MapLibre GL initially. TileLayer handles raster base maps. MapLibre can be added later if vector base maps needed.

## Build & Install (Internal Use)

```bash
# Build JavaScript bundle
npm install
npm run build

# Generate Python classes from React component
npm run build:py

# Install Python package in development mode
pip install -e .
```

## Verification Plan

1. **Build verification:**
   ```bash
   npm run build:all  # Should complete without errors
   pip install -e .   # Should install dash_deckgl package
   ```

2. **Basic rendering test:**
   ```python
   from dash import Dash
   from dash_deckgl import DeckGL

   app = Dash(__name__)
   app.layout = DeckGL(
       id='test',
       layers=[{
           '@@type': 'TileLayer',
           'data': 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
       }],
       initialViewState={'longitude': -122.4, 'latitude': 37.8, 'zoom': 10}
   )
   app.run_server(debug=True)
   ```

3. **Verify in browser:**
   - Map renders with OSM tiles
   - Can pan/zoom
   - Add GeoJSON layer - features display
   - Enable click events - callback fires
   - Test with 100k+ points - renders smoothly

## Comparison: dash-deckgl vs dash-deck

| Feature | dash-deck (pydeck) | dash-deckgl (direct) |
|---------|-------------------|---------------------|
| Dependency | pydeck + deck.gl | deck.gl only |
| TileLayer | Limited/broken | Full support |
| COG support | None | Built-in |
| Performance | JSON overhead | Direct + binary option |
| Layer coverage | Partial | Complete |
| Error handling | Silent failures | Validation + errors |
| Maintenance | Stale (POC) | Active |
