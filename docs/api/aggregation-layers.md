# Aggregation Layers

Aggregation layers from `@deck.gl/aggregation-layers` bin point data into cells and render aggregated values.

```python
from deckgl_dash.layers import HeatmapLayer, HexagonLayer, GridLayer
```

All aggregation layers share a common pattern: they take point data with a position accessor, aggregate points into cells, and render with color and/or elevation based on the aggregated values.

---

## HeatmapLayer

Render a heatmap based on point density. Uses GPU-accelerated kernel density estimation.

```python
HeatmapLayer(
    id='heatmap',
    data=points,
    get_position='@@=coordinates',
    get_weight=1,
    radius_pixels=30,
    intensity=1,
    threshold=0.03,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `data` | `Any` | — | **Required.** Point data source |
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `get_weight` | `accessor` | `1` | Weight of each point |
| `radius_pixels` | `float` | `30` | Kernel radius in pixels |
| `intensity` | `float` | `1` | Intensity multiplier |
| `threshold` | `float` | `0.05` | Minimum density to render (0–1) |
| `color_range` | `list[color]` | — | Array of colors for the gradient |
| `color_domain` | `list[float]` | — | Domain for color mapping |
| `aggregation` | `str` | `'SUM'` | `'SUM'` or `'MEAN'` |
| `pickable` | `bool` | `False` | Enable interactions |
| `opacity` | `float` | `1.0` | Layer opacity |

### With Color Scales

```python
from deckgl_dash import color_range_from_scale

HeatmapLayer(
    id='heatmap',
    data=points,
    get_position='@@=coordinates',
    color_range=color_range_from_scale('plasma', 6),
    radius_pixels=40,
)
```

---

## HexagonLayer

Aggregate data into hexagonal bins with optional 3D extrusion.

```python
HexagonLayer(
    id='hexagons',
    data=points,
    get_position='@@=coordinates',
    radius=1000,
    elevation_scale=100,
    extruded=True,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `data` | `Any` | — | **Required.** Point data source |
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `radius` | `float` | `1000` | Hexagon radius in meters |
| `coverage` | `float` | `1` | Hexagon coverage ratio (0–1) |
| `extruded` | `bool` | `False` | Enable 3D extrusion |
| `elevation_scale` | `float` | `1` | Elevation multiplier |
| `elevation_range` | `list[float]` | `[0, 1000]` | Range for elevation mapping |
| `color_range` | `list[color]` | — | Array of colors for bin coloring |
| `color_domain` | `list[float]` | — | Domain for color mapping |
| `color_scale_type` | `str` | `'quantize'` | `'quantize'`, `'quantile'`, or `'ordinal'` |
| `get_color_weight` | `accessor` | `1` | Weight for color aggregation |
| `color_aggregation` | `str` | `'SUM'` | `'SUM'`, `'MEAN'`, `'MIN'`, or `'MAX'` |
| `get_elevation_weight` | `accessor` | `1` | Weight for elevation aggregation |
| `elevation_aggregation` | `str` | `'SUM'` | `'SUM'`, `'MEAN'`, `'MIN'`, or `'MAX'` |
| `upper_percentile` | `float` | `100` | Hide bins above this percentile |
| `lower_percentile` | `float` | `0` | Hide bins below this percentile |
| `material` | `bool \| dict` | — | 3D lighting material settings |
| `pickable` | `bool` | `False` | Enable interactions |
| `opacity` | `float` | `1.0` | Layer opacity |

### Example with Color Range

```python
from deckgl_dash import color_range_from_scale

HexagonLayer(
    id='hexagons',
    data=points,
    get_position='@@=coordinates',
    radius=500,
    color_range=color_range_from_scale('viridis', 6),
    elevation_scale=50,
    elevation_range=[0, 500],
    extruded=True,
    pickable=True,
)
```

---

## GridLayer

Aggregate data into a square grid. Similar to HexagonLayer but with square cells.

```python
GridLayer(
    id='grid',
    data=points,
    get_position='@@=coordinates',
    cell_size=200,
    elevation_scale=50,
    extruded=True,
    pickable=True,
)
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | — | **Required.** Layer identifier |
| `data` | `Any` | — | **Required.** Point data source |
| `get_position` | `accessor` | — | Position `[lng, lat]` |
| `cell_size` | `float` | `1000` | Grid cell size in meters |
| `coverage` | `float` | `1` | Cell coverage ratio (0–1) |
| `extruded` | `bool` | `False` | Enable 3D extrusion |
| `elevation_scale` | `float` | `1` | Elevation multiplier |
| `elevation_range` | `list[float]` | `[0, 1000]` | Range for elevation mapping |
| `color_range` | `list[color]` | — | Array of colors for bin coloring |
| `color_domain` | `list[float]` | — | Domain for color mapping |
| `color_scale_type` | `str` | `'quantize'` | `'quantize'`, `'quantile'`, or `'ordinal'` |
| `get_color_weight` | `accessor` | `1` | Weight for color aggregation |
| `color_aggregation` | `str` | `'SUM'` | `'SUM'`, `'MEAN'`, `'MIN'`, or `'MAX'` |
| `get_elevation_weight` | `accessor` | `1` | Weight for elevation aggregation |
| `elevation_aggregation` | `str` | `'SUM'` | `'SUM'`, `'MEAN'`, `'MIN'`, or `'MAX'` |
| `upper_percentile` | `float` | `100` | Hide bins above this percentile |
| `lower_percentile` | `float` | `0` | Hide bins below this percentile |
| `material` | `bool \| dict` | — | 3D lighting material settings |
| `pickable` | `bool` | `False` | Enable interactions |
| `opacity` | `float` | `1.0` | Layer opacity |
