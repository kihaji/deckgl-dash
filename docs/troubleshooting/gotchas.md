# Gotchas

Common issues and their fixes.

## Quick Reference

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| `controller` ignored in MapLibre mode | `dragRotate`, `maxPitch` have no effect | Use `map_options` in `MapLibreConfig` |
| Events not firing | `click_info`/`hover_info` never update | Set `enable_events=['click', 'hover']` |
| `interleaved=True` is slow | Pan/zoom lag with MapLibre | Use `interleaved=False` (default) |
| Log scale fails | Colors don't render | Log requires positive values (min > 0) |
| TileLayer blank | No tiles visible | Check URL has `{z}/{x}/{y}` placeholders |
| Hex colors ignored in JSON mode | Colors don't apply | Use `[r, g, b]` arrays in JSON dicts; hex strings only work with Python helpers |
| Layers/view state lost on basemap change | Overlay layers vanish or map jumps to initial position when switching styles | Update `maplibre_config` prop, don't recreate the DeckGL component |
| Slow layer updates | Updating `layers` resends all layer data every time | Use `layer_data` to update individual layers by ID. See [Layer Data Updates](../guides/layer-data-updates.md) |

---

## Detailed Explanations

### controller Ignored in MapLibre Mode

When using `maplibre_config`, the deck.gl `controller` prop is completely bypassed. MapLibre GL JS manages its own map interactions.

=== "Correct"

    ```python
    MapLibreConfig(
        style=MapLibreStyle.CARTO_POSITRON,
        map_options={
            'dragRotate': False,
            'maxPitch': 0,
            'maxZoom': 16,
            'minZoom': 4,
        },
    )
    ```

=== "Incorrect"

    ```python
    # These settings are silently ignored!
    DeckGL(
        maplibre_config=MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON).to_dict(),
        controller={'dragRotate': False, 'maxPitch': 0},  # NO EFFECT
        ...
    )
    ```

### Events Not Firing

Events are **disabled by default** for performance. You must explicitly enable them:

```python
DeckGL(
    id='map',
    enable_events=['click', 'hover'],  # or enable_events=True for all
    ...
)
```

Also ensure the layer has `pickable=True`:

```python
GeoJsonLayer(id='data', data=geojson, pickable=True, ...)
```

### Interleaved Mode Performance

`interleaved=True` forces deck.gl to synchronize rendering with MapLibre on every frame, which can cause visible lag during pan/zoom:

```python
# Default (recommended) — deck.gl layers render on top of MapLibre
MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON)

# Only use if you need deck.gl layers between MapLibre layers (e.g., below labels)
MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON, interleaved=True)
```

### Log Scale Requires Positive Values

The `@@scale(...:log, ...)` modifier uses logarithmic interpolation, which is undefined for zero and negative values:

```python
# Will fail if any value <= 0
ColorScale('OrRd').domain(0, 100).log()  # min=0 is problematic

# Use a positive minimum
ColorScale('OrRd').domain(1, 100).log()  # min=1 works
```

### TileLayer Shows Blank Map

If tiles aren't loading, check:

1. **URL placeholders** — The URL must contain `{z}`, `{x}`, and `{y}`:
   ```python
   # Correct
   TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png')

   # Wrong — missing placeholders
   TileLayer(id='basemap', data='https://tile.openstreetmap.org/tiles')
   ```

2. **CORS** — The tile server must allow cross-origin requests. Most public tile servers (OSM, CARTO) do. Custom servers may need CORS headers.

3. **Zoom range** — If `min_zoom` or `max_zoom` are set incorrectly, tiles won't load at the current zoom level.

### Hex Colors in JSON Mode

Python helper classes automatically convert hex strings (`'#FF8C00'`) to `[r, g, b]` arrays. If you're using raw JSON dicts, you must provide arrays directly:

=== "Python Helpers (hex works)"

    ```python
    GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00')
    ```

=== "JSON Dicts (use arrays)"

    ```python
    {'@@type': 'GeoJsonLayer', 'id': 'data', 'data': geojson, 'getFillColor': [255, 140, 0]}
    ```

### Layers or View State Lost on Basemap Change

When switching basemap styles, update the `maplibre_config` prop on the existing DeckGL component. The component uses `map.setStyle()` internally, which preserves the MapLibre map instance, the deck.gl overlay, all deck.gl data layers, and the camera position. Do **not** recreate the entire component in a callback — that destroys everything and resets from scratch.

=== "Correct — update the prop"

    ```python
    # Callback targets the component's maplibre_config prop
    @callback(Output('map', 'maplibreConfig'), Input('style-picker', 'value'))
    def switch_style(style_url):
        return MapLibreConfig(style=style_url).to_dict()
    ```

=== "Incorrect — recreates the component"

    ```python
    # Callback returns a new DeckGL(...) — view state is lost!
    @callback(Output('map-container', 'children'), Input('style-picker', 'value'))
    def switch_style(style_url):
        return DeckGL(id='map', maplibre_config=MapLibreConfig(style=style_url).to_dict(), ...)
    ```

See the [Switching Basemap Styles](../guides/maplibre-integration.md#switching-basemap-styles) guide for a full example.
