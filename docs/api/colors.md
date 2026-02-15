# Color Scales

deckgl-dash includes data-driven color mapping using chroma.js scales. There are two approaches:

1. **`ColorScale`** — Fluent API generating `@@scale()` accessor strings for per-feature coloring
2. **`color_range_from_scale()`** — Generate discrete color arrays for aggregation layers

```python
from deckgl_dash import ColorScale, color_range_from_scale, AVAILABLE_SCALES
```

---

## ColorScale

Build `@@scale()` accessor strings with a fluent (chainable) API. The scale is evaluated on the client side by chroma.js.

### Basic Usage

```python
from deckgl_dash import ColorScale
from deckgl_dash.layers import GeoJsonLayer

scale = ColorScale('viridis').domain(0, 100)

layer = GeoJsonLayer(
    id='choropleth',
    data=geojson,
    get_fill_color=scale.accessor('properties.value'),
    pickable=True,
)
# get_fill_color = '@@scale(viridis, properties.value, 0, 100)'
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `ColorScale(name)` | Create a scale from a named palette | `ColorScale` |
| `.domain(min, max)` | Set explicit value range. If omitted, auto-detected from data | `self` |
| `.alpha(value)` | Set opacity (0–255). Default 255 (opaque) | `self` |
| `.reverse()` | Reverse color direction | `self` |
| `.log()` | Logarithmic interpolation (for exponential distributions) | `self` |
| `.sqrt()` | Square root interpolation (less extreme than log) | `self` |
| `.accessor(property)` | Generate the `@@scale(...)` string for a data property | `str` |

!!! warning "Log scale requires positive values"
    When using `.log()`, all data values must be positive (`> 0`). Values at or below zero will cause rendering issues. See [Gotchas](../troubleshooting/gotchas.md).

### Examples

```python
# Basic scale with explicit domain
ColorScale('viridis').domain(0, 100).accessor('properties.value')
# '@@scale(viridis, properties.value, 0, 100)'

# Reversed scale with transparency
ColorScale('plasma').domain(0, 1000).alpha(180).reverse().accessor('properties.count')
# '@@scale(plasma:reverse, properties.count, 0, 1000, 180)'

# Log scale for exponential data
ColorScale('OrRd').domain(1, 10000).log().accessor('properties.population')
# '@@scale(OrRd:log, properties.population, 1, 10000)'

# Square root scale
ColorScale('Blues').domain(0, 500).sqrt().accessor('properties.depth')
# '@@scale(Blues:sqrt, properties.depth, 0, 500)'

# Auto-domain (detected from data at render time)
ColorScale('magma').accessor('properties.temperature')
# '@@scale(magma, properties.temperature)'
```

---

## @@scale() Syntax Reference

The `@@scale()` accessor string format (for use in raw JSON dicts):

```
@@scale(scaleName[:modifier[:modifier]], propertyPath[, min, max[, alpha]])
```

| Part | Required | Description |
|------|----------|-------------|
| `scaleName` | Yes | Chroma.js scale name (e.g., `viridis`, `plasma`) |
| `:modifier` | No | `log`, `sqrt`, `reverse` — can be chained with `:` |
| `propertyPath` | Yes | Dot-separated path to data property |
| `min` | No | Minimum domain value (auto-detected if omitted) |
| `max` | No | Maximum domain value (auto-detected if omitted) |
| `alpha` | No | Opacity 0–255 (default 255) |

Examples in raw JSON:

```python
# In a JSON dict layer
{
    '@@type': 'GeoJsonLayer',
    'getFillColor': '@@scale(viridis, properties.value, 0, 100)',
    'getLineColor': '@@scale(Reds:reverse, properties.risk, 0, 1, 200)',
}
```

---

## color_range_from_scale()

Generate a discrete list of `[r, g, b]` colors from a named scale. Used with aggregation layers that accept a `color_range` prop.

```python
from deckgl_dash import color_range_from_scale

colors = color_range_from_scale('viridis', 6)
# [[68, 1, 84], [59, 82, 139], [33, 144, 140], [93, 201, 99], [253, 231, 37], ...]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scale_name` | `str` | — | **Required.** Scale name (e.g., `'viridis'`) |
| `steps` | `int` | `6` | Number of colors to generate |
| `reverse` | `bool` | `False` | Reverse the color order |

### Usage with Aggregation Layers

```python
from deckgl_dash import color_range_from_scale
from deckgl_dash.layers import HexagonLayer

HexagonLayer(
    id='hexagons',
    data=points,
    get_position='@@=coordinates',
    color_range=color_range_from_scale('viridis', 6),
    radius=500,
    extruded=True,
)
```

---

## Available Scales

### Sequential

`OrRd`, `PuBu`, `BuPu`, `Oranges`, `BuGn`, `YlOrBr`, `YlGn`, `Reds`, `RdPu`, `Greens`, `YlGnBu`, `Purples`, `GnBu`, `Greys`, `YlOrRd`, `PuRd`, `Blues`, `PuBuGn`

### Diverging

`Spectral`, `RdYlGn`, `RdBu`, `PiYG`, `PRGn`, `RdYlBu`, `BrBG`, `RdGy`, `PuOr`

### Perceptually Uniform

`viridis`, `plasma`, `inferno`, `magma`, `cividis`, `turbo`

All scale names are available in the `AVAILABLE_SCALES` tuple:

```python
from deckgl_dash import AVAILABLE_SCALES
print(AVAILABLE_SCALES)
```
