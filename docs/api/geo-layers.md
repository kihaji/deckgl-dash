# Geo Layers

Geo layers from `@deck.gl/geo-layers` handle tile-based data and geographic projections.

```python
from deckgl_dash.layers import TileLayer, MVTLayer, BitmapLayer
```

---

## TileLayer

Render tiled data from XYZ tile servers. Commonly used for raster basemaps (OSM, CARTO, etc.).

```python
TileLayer(
    id='basemap',
    data='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    min_zoom=0,
    max_zoom=19,
)
```

!!! tip "URL format"
    The `data` URL must include `{z}`, `{x}`, and `{y}` placeholders. If tiles appear blank, verify these placeholders are present and the tile server is accessible.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `data` | `str` | — | **Required.** Tile URL template with `{z}/{x}/{y}` placeholders |
| `tile_size` | `int` | `512` | Tile size in pixels |
| `min_zoom` | `int` | `0` | Minimum zoom level to fetch tiles |
| `max_zoom` | `int` | — | Maximum zoom level to fetch tiles |
| `max_cache_size` | `int` | — | Maximum number of tiles to cache |
| `max_cache_byte_size` | `int` | — | Maximum cache size in bytes |
| `refinement_strategy` | `str` | `'best-available'` | `'best-available'`, `'no-overlap'`, or `'never'` |
| `extent` | `list[float]` | — | Bounding box `[minX, minY, maxX, maxY]` |
| `max_requests` | `int` | `6` | Maximum concurrent tile requests |
| `pickable` | `bool` | `False` | Enable interactions |
| `opacity` | `float` | `1.0` | Layer opacity |
| `visible` | `bool` | `True` | Show/hide layer |

---

## MVTLayer

Render Mapbox Vector Tiles (MVT/PBF) with styling. Extends TileLayer with GeoJsonLayer-like styling.

```python
MVTLayer(
    id='vector-tiles',
    data='https://tiles.example.com/{z}/{x}/{y}.mvt',
    get_fill_color='@@=properties.color',
    get_line_color=[0, 0, 0],
    get_line_width=1,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `data` | `str` | — | **Required.** MVT tile URL template |
| `unique_id_property` | `str` | — | Property to use as unique feature ID |
| `highlighted_feature_id` | `Any` | — | ID of feature to highlight |
| `filled` | `bool` | `True` | Render filled areas |
| `stroked` | `bool` | `True` | Render outlines |
| `extruded` | `bool` | `False` | Enable 3D extrusion |
| `point_type` | `str` | `'circle'` | Point rendering type |
| `get_fill_color` | `color` | `[0,0,0,255]` | Fill color |
| `get_line_color` | `color` | `[0,0,0,255]` | Line/outline color |
| `get_line_width` | `accessor` | `1` | Line width |
| `get_point_radius` | `accessor` | `1` | Point radius |
| `get_elevation` | `accessor` | `0` | Extrusion height |
| `binary` | `bool` | `False` | Use binary data format (faster for large datasets) |

MVTLayer also inherits all TileLayer props (`tile_size`, `min_zoom`, `max_zoom`, etc.) and size scale props (`line_width_units`, `point_radius_units`, etc.).

---

## BitmapLayer

Render a single bitmap image at specified geographic bounds.

```python
BitmapLayer(
    id='satellite',
    image='https://example.com/image.png',
    bounds=[-122.5, 37.5, -122.0, 38.0],  # [west, south, east, north]
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `image` | `str` | — | URL of the image to render |
| `bounds` | `list[float]` | — | Geographic bounds `[west, south, east, north]` |
| `tint_color` | `color` | `[255,255,255]` | Tint color applied to the image |
| `desaturate` | `float` | `0` | Desaturation amount (0 = full color, 1 = grayscale) |
| `transparent_color` | `color` | `[0,0,0,0]` | Color to render as transparent |
| `pickable` | `bool` | `False` | Enable interactions |
| `opacity` | `float` | `1.0` | Layer opacity |
| `visible` | `bool` | `True` | Show/hide layer |
