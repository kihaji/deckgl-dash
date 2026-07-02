# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`delete` drawing mode** — click-to-delete: activate the mode once, then each click on a feature deletes it immediately (no prior selection needed). Deletions sync back to Python via the existing drawing event path; the `deleteSelected` flag mechanism remains for backward compatibility.

## [0.10.0] - 2026-06-14

### Added
- **Time slider with GPU-filtered sliding-window animation** — filter visible map data to a sliding time window and animate it across the full time range, entirely client-side. Filtering runs on the GPU via deck.gl's `DataFilterExtension`; playback is driven by an internal `requestAnimationFrame` loop, so the map updates at 60fps with no per-frame server round trips.
- **`time_filter` input prop and `current_time` output prop** — configure the window/domain/playback and receive a throttled playback head time back in Dash callbacks.
- **`compute_time_domain` and `build_time_filter` helpers** — Python-side utilities for constructing time filter configurations from data.
- `extensions` entries in layer JSON (e.g. `'DataFilterExtension'`) are instantiated by the layer registry; layers with a `get_filter_value` accessor auto-attach the extension.
- `DirectedPathLayer` forwards the time filter so paths and their direction arrows fade together.

## [0.9.0] - 2026-06-13

### Added
- **`MultiColorPathLayer`** — per-segment path coloring via `PathLayer(multi_color=True)` with a per-segment color accessor.
- **`DirectedPathLayer`** — direction-of-movement arrows along paths via `PathLayer(show_direction=True)`, with `arrow_spacing`/`arrow_size` options; composes with `multi_color`.
- **`fit_bounds` prop and `compute_bounds` helper** — viewport-aware camera fitting to a bounding box in both deck-only and MapLibre modes.
- List → click-to-highlight example (`examples/`), pairing a feature list with map highlighting.

## [0.8.0] - 2026-04-04

### Added
- **Drawing and editing on layers** — new `drawing_config` prop (mode + style), `drawing_features` input/output prop (GeoJSON FeatureCollection), and `drawing_event` output prop, backed by `@deck.gl-community/editable-layers`. Includes `DrawingConfig`/`DrawingStyle` helpers, `DRAWING_MODES`, drawing demo, and guides.
- **`layer_order` prop** — control layer rendering order with a list of layer IDs (bottom to top); documented in the layer-ordering guide.

## [0.7.0] - 2026-04-02

### Added
- **`load_options` prop** on all layer types — configure how remote data is fetched, including credentials, headers, and CORS mode. Enables client-side loading of GeoJSON from external servers with browser client certificate (mTLS) support.
- **`dataLoad` and `dataLoadError` events** — opt-in via `enable_events=['dataLoad', 'dataLoadError']` to receive Dash callbacks when layers load or fail to load remote data.
- **`data_load_info` output prop** — contains `layerId`, `featureCount`, and `timestamp` after a successful remote data load.
- **`data_load_error` output prop** — contains `layerId`, `error`, and `timestamp` when a remote data load fails.
- **Coordinate click support** — click handler reports map coordinates, plus a `CoordinateConverter` utility (`deckgl_dash.coordinates`) for converting between coordinate systems (lat/lon, UTM, MGRS); coordinate click demo included.

## [0.6.0] - 2026-03-15

### Fixed
- Multiple layers can now be updated independently via `layer_data` — per-layer updates no longer clobber data previously sent for other layers.

## [0.5.0] - 2026-03-01

### Added
- **`layer_data` prop** — per-layer data overrides via `{layer_id: data}` dict. Update individual layer data without resending the entire `layers` array. Works with Dash `Patch()` for independent multi-layer updates.
- New documentation guide: [Layer Data Updates](docs/guides/layer-data-updates.md)

### Changed
- `hexagon_deferred_load_demo.py` — rewritten to use `layer_data` instead of `dcc.Store` + full layer rebuild
- `performance_test_demo.py` — HexagonLayer toggles now use `layer_data` + `Patch()` for independent updates

## [0.4.0] - 2026-02-15

### Added
- MkDocs Material documentation site

### Fixed
- Preserve deck.gl overlay layers on basemap style change (#7)
- Preserve MapLibre view state on basemap style change (#6)

## [0.3.0 – 0.3.5] - 2026-01-28

### Added
- **MapLibre GL JS integration** (`maplibre_config` prop) — vector-tile basemaps rendered by MapLibre with deck.gl layers as an overlay (0.3.0)

### Fixed
- 0.3.1–0.3.5: packaging/build-pipeline fixes — optional dependency handling, build artifacts included in the wheel, Makefile updates

## [0.2.0] - 2026-01-26

### Added
- `scripts/release.py` release helper (bump version, build, commit, tag)

### Changed
- Package metadata updates; removed an obsolete browser test

## [0.1.0] - 2026-01-25

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
