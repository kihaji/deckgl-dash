# Core Layers

Core layers from `@deck.gl/layers` cover the most common visualization types.

```python
from deckgl_dash.layers import (
    GeoJsonLayer, ScatterplotLayer, PathLayer, LineLayer,
    ArcLayer, IconLayer, TextLayer, PolygonLayer,
)
```

## Common Props

All layers share these properties:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Unique layer identifier |
| `data` | `Any` | — | **Required.** Data source (URL, GeoJSON dict, or list of records) |
| `pickable` | `bool` | `False` | Enable hover/click interactions |
| `opacity` | `float` | `1.0` | Layer opacity (0–1) |
| `visible` | `bool` | `True` | Show/hide the layer |
| `auto_highlight` | `bool` | `False` | Highlight features on hover |
| `highlight_color` | `color` | `[0,0,128,128]` | Color used for auto-highlight |

### Color Values

Colors can be specified as:

- RGB list: `[255, 140, 0]`
- RGBA list: `[255, 140, 0, 200]`
- Hex string: `'#FF8C00'` (auto-converted to RGB)
- Accessor: `'@@=properties.color'`
- Scale: `ColorScale('viridis').domain(0, 100).accessor('properties.value')`

### Accessor Syntax

Use `@@=` to reference data properties:

```python
get_fill_color='@@=properties.color'    # Access nested property
get_radius='@@=radius'                   # Access top-level property
```

---

## GeoJsonLayer

Render GeoJSON features (points, lines, polygons). Automatically detects geometry type.

```python
GeoJsonLayer(
    id='geojson',
    data='https://example.com/data.geojson',
    get_fill_color=[255, 140, 0, 200],
    get_line_color='#000000',
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `filled` | `bool` | `True` | Render filled areas |
| `stroked` | `bool` | `True` | Render outlines |
| `extruded` | `bool` | `False` | Enable 3D extrusion |
| `wireframe` | `bool` | `False` | Show wireframe in extruded mode |
| `point_type` | `str` | `'circle'` | Point rendering: `'circle'`, `'icon'`, `'text'` |
| `get_fill_color` | `color` | `[0,0,0,255]` | Fill color |
| `get_line_color` | `color` | `[0,0,0,255]` | Outline color |
| `get_line_width` | `accessor` | `1` | Line width |
| `get_point_radius` | `accessor` | `1` | Point radius |
| `get_elevation` | `accessor` | `0` | Extrusion height |
| `line_width_units` | `str` | `'meters'` | `'meters'`, `'common'`, or `'pixels'` |
| `line_width_min_pixels` | `float` | `0` | Minimum line width in pixels |
| `point_radius_units` | `str` | `'meters'` | `'meters'`, `'common'`, or `'pixels'` |
| `point_radius_min_pixels` | `float` | `0` | Minimum point radius in pixels |
| `elevation_scale` | `float` | `1` | Multiplier for elevation values |

---

## ScatterplotLayer

Render circles at given coordinates. Optimized for large datasets (millions of points).

```python
ScatterplotLayer(
    id='scatter',
    data=points_data,
    get_position='@@=coordinates',
    get_radius=100,
    get_fill_color=[255, 0, 0],
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `filled` | `bool` | `True` | Render filled circles |
| `stroked` | `bool` | `False` | Render circle outlines |
| `get_radius` | `accessor` | `1` | Circle radius |
| `get_fill_color` | `color` | `[0,0,0,255]` | Fill color |
| `get_line_color` | `color` | `[0,0,0,255]` | Outline color |
| `get_line_width` | `accessor` | `1` | Outline width |
| `radius_units` | `str` | `'meters'` | `'meters'`, `'common'`, or `'pixels'` |
| `radius_scale` | `float` | `1` | Radius multiplier |
| `radius_min_pixels` | `float` | `0` | Minimum radius in pixels |
| `radius_max_pixels` | `float` | `inf` | Maximum radius in pixels |
| `billboard` | `bool` | `False` | Always face camera |
| `anti_aliasing` | `bool` | `True` | Enable anti-aliasing |

---

## PathLayer

Render paths/polylines from coordinate arrays.

```python
PathLayer(
    id='paths',
    data=routes,
    get_path='@@=coordinates',
    get_color=[0, 100, 200],
    get_width=5,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_path` | `accessor` | — | Array of `[lng, lat]` coordinates |
| `get_color` | `color` | `[0,0,0,255]` | Path color |
| `get_width` | `accessor` | `1` | Path width |
| `width_units` | `str` | `'meters'` | `'meters'`, `'common'`, or `'pixels'` |
| `width_min_pixels` | `float` | `0` | Minimum width in pixels |
| `width_max_pixels` | `float` | `inf` | Maximum width in pixels |
| `cap_rounded` | `bool` | `False` | Rounded line caps |
| `joint_rounded` | `bool` | `False` | Rounded line joints |
| `billboard` | `bool` | `False` | Always face camera |

---

## LineLayer

Render straight lines between source and target points.

```python
LineLayer(
    id='connections',
    data=connections,
    get_source_position='@@=source',
    get_target_position='@@=target',
    get_color=[100, 100, 100],
    get_width=2,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_source_position` | `accessor` | — | Start point `[lng, lat]` |
| `get_target_position` | `accessor` | — | End point `[lng, lat]` |
| `get_color` | `color` | `[0,0,0,255]` | Line color |
| `get_width` | `accessor` | `1` | Line width |
| `width_units` | `str` | `'pixels'` | `'meters'`, `'common'`, or `'pixels'` |
| `width_min_pixels` | `float` | `0` | Minimum width in pixels |

---

## ArcLayer

Render raised arcs between source and target points. Great for flow visualization.

```python
ArcLayer(
    id='flights',
    data=flights,
    get_source_position='@@=origin',
    get_target_position='@@=destination',
    get_source_color=[0, 128, 200],
    get_target_color=[200, 0, 80],
    get_width=2,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_source_position` | `accessor` | — | Start point `[lng, lat]` |
| `get_target_position` | `accessor` | — | End point `[lng, lat]` |
| `get_source_color` | `color` | `[0,0,0,255]` | Arc color at source |
| `get_target_color` | `color` | `[0,0,0,255]` | Arc color at target |
| `get_width` | `accessor` | `1` | Arc width in pixels |
| `get_height` | `accessor` | `1` | Arc height (0 = flat, 1 = semicircle) |
| `get_tilt` | `accessor` | `0` | Tilt angle in degrees |
| `great_circle` | `bool` | `False` | Use great circle arcs |
| `num_segments` | `int` | `50` | Number of segments per arc |

---

## IconLayer

Render icons/markers at given coordinates.

```python
IconLayer(
    id='markers',
    data=locations,
    get_position='@@=coordinates',
    get_icon='@@=icon',
    icon_atlas='https://example.com/icons.png',
    icon_mapping={'marker': {'x': 0, 'y': 0, 'width': 128, 'height': 128}},
    get_size=40,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `icon_atlas` | `str` | — | URL of the icon sprite sheet |
| `icon_mapping` | `dict` | — | Mapping of icon names to sprite positions |
| `get_icon` | `accessor` | — | Icon name or accessor |
| `get_size` | `accessor` | `1` | Icon size |
| `get_color` | `color` | `[0,0,0,255]` | Icon tint color |
| `get_angle` | `accessor` | `0` | Rotation angle in degrees |
| `size_units` | `str` | `'pixels'` | `'meters'`, `'common'`, or `'pixels'` |
| `size_scale` | `float` | `1` | Size multiplier |
| `billboard` | `bool` | `True` | Always face camera |
| `alpha_cutoff` | `float` | `0.05` | Discard pixels with alpha below this |

---

## TextLayer

Render text labels at given coordinates.

```python
TextLayer(
    id='labels',
    data=cities,
    get_position='@@=coordinates',
    get_text='@@=name',
    get_size=16,
    get_color=[0, 0, 0],
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `get_text` | `accessor` | — | Text string |
| `get_size` | `accessor` | `32` | Font size |
| `get_color` | `color` | `[0,0,0,255]` | Text color |
| `get_angle` | `accessor` | `0` | Rotation angle |
| `get_text_anchor` | `accessor` | `'middle'` | Horizontal alignment |
| `get_alignment_baseline` | `accessor` | `'center'` | Vertical alignment |
| `font_family` | `str` | `'Monaco, monospace'` | CSS font family |
| `font_weight` | `str \| int` | `'normal'` | CSS font weight |
| `size_units` | `str` | `'pixels'` | `'meters'`, `'common'`, or `'pixels'` |
| `background` | `bool` | `False` | Show background rectangle |
| `background_color` | `color` | `[255,255,255,255]` | Background color |
| `billboard` | `bool` | `True` | Always face camera |
| `outline_width` | `float` | `0` | Text outline width |
| `outline_color` | `color` | `[0,0,0,255]` | Text outline color |

---

## PolygonLayer

Render filled and/or stroked polygons from coordinate arrays.

```python
PolygonLayer(
    id='polygons',
    data=regions,
    get_polygon='@@=coordinates',
    get_fill_color=[255, 140, 0, 200],
    get_line_color=[0, 0, 0],
    get_line_width=2,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `get_polygon` | `accessor` | — | Polygon coordinate ring(s) |
| `filled` | `bool` | `True` | Render filled area |
| `stroked` | `bool` | `True` | Render outline |
| `extruded` | `bool` | `False` | Enable 3D extrusion |
| `wireframe` | `bool` | `False` | Show wireframe |
| `get_fill_color` | `color` | `[0,0,0,255]` | Fill color |
| `get_line_color` | `color` | `[0,0,0,255]` | Outline color |
| `get_line_width` | `accessor` | `1` | Outline width |
| `get_elevation` | `accessor` | `0` | Extrusion height |
| `elevation_scale` | `float` | `1` | Elevation multiplier |
| `line_width_units` | `str` | `'meters'` | `'meters'`, `'common'`, or `'pixels'` |
