# MapLibre API

Python helper classes for configuring MapLibre GL JS basemaps with deck.gl overlays.

```python
from deckgl_dash.maplibre import (
    MapLibreConfig, MapLibreStyle,
    RasterSource, VectorSource, GeoJSONSource,
    FillLayer, LineLayer, RasterLayer, CircleLayer, SymbolLayer, FillExtrusionLayer,
)
```

---

## MapLibreConfig

Main configuration class. Pass `config.to_dict()` to the `maplibre_config` prop of `DeckGL`.

```python
config = MapLibreConfig(
    style=MapLibreStyle.CARTO_POSITRON,
    map_options={'maxPitch': 60},
)
DeckGL(maplibre_config=config.to_dict(), ...)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `style` | `str \| dict` | — | **Required.** MapLibre style URL or inline style spec dict |
| `sources` | `dict[str, Source]` | `{}` | Additional sources: `{source_id: RasterSource(...)}` |
| `map_layers` | `list[Layer]` | `[]` | Additional MapLibre layers to render |
| `interleaved` | `bool` | `False` | Interleave deck.gl and MapLibre layers |
| `attribution_control` | `bool` | `True` | Show attribution control |
| `map_options` | `dict` | `{}` | Options passed to the MapLibre Map constructor |

!!! warning "`controller` is ignored"
    Use `map_options` to control map interactions (drag, zoom, pitch limits) when in MapLibre mode. The `controller` prop on `DeckGL` has no effect. See [MapLibre Integration Guide](../guides/maplibre-integration.md#controller-gotcha).

### map_options Reference

Common `map_options` keys (passed directly to MapLibre):

| Key | Type | Description |
|-----|------|-------------|
| `maxZoom` | `float` | Maximum zoom level |
| `minZoom` | `float` | Minimum zoom level |
| `maxPitch` | `float` | Maximum pitch in degrees |
| `maxBounds` | `list` | `[[sw_lng, sw_lat], [ne_lng, ne_lat]]` |
| `dragRotate` | `bool` | Enable rotation by dragging |
| `scrollZoom` | `bool` | Enable zoom by scrolling |
| `doubleClickZoom` | `bool` | Enable zoom by double-clicking |

---

## MapLibreStyle

Pre-defined style URL constants.

| Constant | Provider | Description |
|----------|----------|-------------|
| `MapLibreStyle.CARTO_POSITRON` | CARTO | Light theme (no API key) |
| `MapLibreStyle.CARTO_DARK_MATTER` | CARTO | Dark theme (no API key) |
| `MapLibreStyle.CARTO_VOYAGER` | CARTO | Colorful theme (no API key) |
| `MapLibreStyle.OPENFREEMAP_LIBERTY` | OpenFreeMap | Liberty style (no API key) |
| `MapLibreStyle.OPENFREEMAP_BRIGHT` | OpenFreeMap | Bright style (no API key) |
| `MapLibreStyle.OPENFREEMAP_POSITRON` | OpenFreeMap | Positron style (no API key) |
| `MapLibreStyle.MAPTILER_STREETS` | MapTiler | Streets (requires API key) |
| `MapLibreStyle.MAPTILER_BASIC` | MapTiler | Basic (requires API key) |
| `MapLibreStyle.MAPTILER_SATELLITE` | MapTiler | Satellite (requires API key) |
| `MapLibreStyle.MAPTILER_HYBRID` | MapTiler | Hybrid (requires API key) |
| `MapLibreStyle.MAPTILER_OUTDOOR` | MapTiler | Outdoor (requires API key) |

### Empty Style

Use `MapLibreStyle.empty()` for maps with only custom sources (no basemap):

```python
config = MapLibreConfig(style=MapLibreStyle.empty(), sources={...}, map_layers=[...])
```

---

## Source Classes

### RasterSource

Raster tile source for XYZ tile servers or WMS endpoints.

```python
# XYZ tiles
source = RasterSource(
    tiles=['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
    tile_size=256,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tiles` | `list[str]` | `[]` | Tile URL templates with `{z}/{x}/{y}` placeholders |
| `tile_size` | `int` | `256` | Tile size in pixels |
| `min_zoom` | `int` | `0` | Minimum zoom level |
| `max_zoom` | `int` | `22` | Maximum zoom level |
| `bounds` | `list[float]` | — | Bounding box `[west, south, east, north]` |
| `attribution` | `str` | — | Attribution string |
| `scheme` | `str` | `'xyz'` | `'xyz'` or `'tms'` |

#### RasterSource.from_wms()

Factory method for WMS endpoints. Builds the full GetMap URL automatically.

```python
source = RasterSource.from_wms(
    base_url='https://ows.terrestris.de/osm/service',
    layers='TOPO-WMS',
    tile_size=256,
    format='image/png',
    transparent=True,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | — | **Required.** WMS service URL |
| `layers` | `str` | — | **Required.** WMS layer name(s), comma-separated |
| `tile_size` | `int` | `256` | Tile size in pixels |
| `format` | `str` | `'image/png'` | Image format |
| `transparent` | `bool` | `True` | Request transparent background |
| `version` | `str` | `'1.1.1'` | WMS version |
| `crs` | `str` | `'EPSG:3857'` | Coordinate reference system |
| `styles` | `str` | `''` | WMS styles parameter |
| `extra_params` | `dict[str, str]` | — | Additional WMS query parameters |

### VectorSource

Vector tile source for PBF/MVT tiles.

```python
# From tile URL
source = VectorSource(tiles=['https://example.com/{z}/{x}/{y}.pbf'])

# From TileJSON
source = VectorSource(url='https://example.com/tiles.json')
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tiles` | `list[str]` | — | Tile URL templates |
| `url` | `str` | — | TileJSON URL (alternative to tiles) |
| `min_zoom` | `int` | `0` | Minimum zoom level |
| `max_zoom` | `int` | `22` | Maximum zoom level |
| `bounds` | `list[float]` | — | Bounding box |
| `attribution` | `str` | — | Attribution string |
| `scheme` | `str` | `'xyz'` | `'xyz'` or `'tms'` |
| `promoteId` | `str \| dict` | — | Property to use as feature ID |

### GeoJSONSource

GeoJSON source for inline or remote GeoJSON data.

```python
# Inline data
source = GeoJSONSource(data={'type': 'FeatureCollection', 'features': [...]})

# Remote URL
source = GeoJSONSource(data='https://example.com/data.geojson')
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `str \| dict` | — | **Required.** GeoJSON dict or URL string |
| `cluster` | `bool` | `False` | Enable point clustering |
| `cluster_radius` | `int` | `50` | Cluster radius in pixels |
| `cluster_max_zoom` | `int` | — | Max zoom for clustering |
| `cluster_min_points` | `int` | `2` | Min points per cluster |
| `cluster_properties` | `dict` | — | Custom cluster aggregation expressions |
| `generate_id` | `bool` | `False` | Auto-generate feature IDs |

---

## MapLibre Layer Classes

These are MapLibre GL JS style layers (not deck.gl layers). They style data from MapLibre sources.

All layer classes share these base parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str` | — | **Required.** Unique layer ID |
| `source` | `str` | — | **Required.** Source ID to use |
| `source_layer` | `str` | — | Source layer name (required for vector sources) |
| `min_zoom` | `float` | — | Minimum zoom for visibility |
| `max_zoom` | `float` | — | Maximum zoom for visibility |
| `filter` | `list` | — | MapLibre filter expression |
| `layout` | `dict` | `{}` | Layout properties |
| `paint` | `dict` | `{}` | Paint properties |

### FillLayer

Filled polygons.

```python
FillLayer(
    id='buildings',
    source='vector-tiles',
    source_layer='building',
    fill_color='#ff0000',
    fill_opacity=0.5,
)
```

Paint shortcuts: `fill_color`, `fill_opacity`, `fill_outline_color`, `fill_pattern`, `fill_antialias`.

### LineLayer

Lines and polygon outlines.

```python
LineLayer(
    id='roads',
    source='vector-tiles',
    source_layer='road',
    line_color='#000000',
    line_width=2,
)
```

Paint shortcuts: `line_color`, `line_width`, `line_opacity`, `line_blur`, `line_dasharray`, `line_gap_width`.
Layout shortcuts: `line_cap`, `line_join`.

### RasterLayer

Raster tile display.

```python
RasterLayer(id='satellite', source='satellite-tiles', raster_opacity=0.8)
```

Paint shortcuts: `raster_opacity`, `raster_hue_rotate`, `raster_brightness_min`, `raster_brightness_max`, `raster_saturation`, `raster_contrast`, `raster_resampling`.

### CircleLayer

Points as circles.

```python
CircleLayer(
    id='points',
    source='geojson-points',
    circle_radius=6,
    circle_color='#007cbf',
)
```

Paint shortcuts: `circle_radius`, `circle_color`, `circle_blur`, `circle_opacity`, `circle_stroke_width`, `circle_stroke_color`.

### SymbolLayer

Text labels and icons.

```python
SymbolLayer(
    id='labels',
    source='places',
    text_field=['get', 'name'],
    text_size=12,
    text_color='#000000',
)
```

Layout shortcuts: `text_field`, `text_size`, `text_font`, `text_anchor`, `icon_image`, `icon_size`, `symbol_placement`.
Paint shortcuts: `text_color`, `text_opacity`, `text_halo_color`, `text_halo_width`, `icon_color`, `icon_opacity`.

### FillExtrusionLayer

3D extruded polygons.

```python
FillExtrusionLayer(
    id='buildings-3d',
    source='vector-tiles',
    source_layer='building',
    fill_extrusion_color='#aaa',
    fill_extrusion_height=['get', 'height'],
    fill_extrusion_base=['get', 'min_height'],
    fill_extrusion_opacity=0.6,
)
```

Paint shortcuts: `fill_extrusion_color`, `fill_extrusion_opacity`, `fill_extrusion_height`, `fill_extrusion_base`, `fill_extrusion_pattern`, `fill_extrusion_vertical_gradient`.
