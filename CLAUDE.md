# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

dash-deckgl is a custom Dash component that wraps deck.gl directly (without pydeck) for high-performance web mapping. Target: internal use, not public PyPI release.

**Key features**: Large vector datasets (1M+ items at 60fps), Cloud Optimized GeoTIFFs (COGs), tile-based base maps, full deck.gl layer catalog.

## Current Status

Research/planning phase. See `DeckGL_Wrapper.md` for complete architecture design, API specifications, and implementation roadmap.

## Build Commands (Once Implemented)

```bash
# Build JavaScript bundle
npm install
npm run build

# Generate Python classes from React component
npm run build:py

# Install Python package in development mode
pip install -e .

# Combined build
npm run build:all
```

## Architecture

### Design Philosophy
- **JSON/Dict-based core**: Direct deck.gl JSON format with `@@type` syntax
- **Python helper classes**: Ergonomic layer constructors (no pydeck dependency)
- **MVP base maps**: TileLayer with raster tiles (OSM, CARTO); MapLibre GL can be added later

### Directory Structure (Planned)
```
dash-deckgl/
├── dash_deckgl/           # Python package
│   ├── DeckGL.py          # Auto-generated Dash component
│   └── layers/            # Python helper classes (base, core, geo, aggregation, raster)
├── src/lib/
│   ├── components/        # DeckGL.react.js - main React component
│   └── utils/             # layerRegistry.js, eventHandler.js
├── examples/
└── tests/
```

### Key Dependencies
- **JavaScript**: @deck.gl/core, @deck.gl/layers, @deck.gl/geo-layers, @deck.gl/aggregation-layers, @deck.gl/react (~9.0), @developmentseed/deck.gl-geotiff
- **Python**: dash >= 2.0.0

## Python API

Two usage options:
1. **Pure JSON**: Direct deck.gl JSON format with `@@type` layer specification
2. **Python helpers**: `from dash_deckgl.layers import GeoJsonLayer, TileLayer`

## Implementation Phases

1. Project setup & core component (layer registry, view state, events)
2. Python layer helpers
3. COG/raster support
4. Examples & testing

## Performance Notes

- Events disabled by default (opt-in with `enableEvents` prop)
- Support binary data transport for large datasets
- GPU-accelerated rendering

## Python Code Styling
- Minimize vertical spacing, use up to 150 characters in a line.
- Ensure all assignment operators "=" have a space on both sides. This includes in parameter lists as well.
- Write tests cases where possible

## Python General
- Use Poetry for virtual environment and python dependency management

## Git Usage
- Use feature branches for all new features.

