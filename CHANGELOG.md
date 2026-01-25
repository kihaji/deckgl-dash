# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-25

### Added
- Initial release of deckgl-dash
- DeckGL Dash component wrapping deck.gl for high-performance WebGL visualization
- Python layer helper classes: `TileLayer`, `GeoJsonLayer`, `ScatterplotLayer`, `HexagonLayer`, `BitmapLayer`, and more
- Support for JSON/dict layer configuration with `@@type` syntax
- `ColorScale` utility for data-driven color mapping
- Event support: click, hover, viewStateChange (opt-in via `enable_events`)
- Tooltip support with customizable HTML templates
- Full controller options for map interactions

### Features
- High-performance rendering for 1M+ data points at 60fps
- Tile-based base maps (OSM, CARTO, custom tile servers)
- All deck.gl layer types supported via JSON configuration
- Snake_case Python API with automatic camelCase conversion
