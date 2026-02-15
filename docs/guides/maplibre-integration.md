# MapLibre Integration

deckgl-dash can use [MapLibre GL JS](https://maplibre.org/) as the basemap renderer, with deck.gl layers rendered as overlays. This gives you access to vector tile basemaps with full styling control.

## Why MapLibre Mode?

| Feature | Standard Mode (TileLayer) | MapLibre Mode |
|---------|---------------------------|---------------|
| Basemap type | Raster tiles only | Vector + raster tiles |
| Basemap styling | None | Full MapLibre style spec |
| Labels | Baked into tiles | Separately rendered, customizable |
| Custom sources | Not supported | Raster, vector, GeoJSON sources |
| Performance | Fastest | Slightly more overhead |

## Basic Setup

```python
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

app.layout = DeckGL(
    id='map',
    maplibre_config=MapLibreConfig(
        style=MapLibreStyle.CARTO_POSITRON,
    ).to_dict(),
    layers=[
        GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF5722', pickable=True),
    ],
    initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
)
```

## Controller Gotcha

!!! danger "The `controller` prop is ignored in MapLibre mode"
    When using `maplibre_config`, the `controller` prop on the DeckGL component has **no effect**. Map interactions (drag, zoom, pitch, rotation limits) are controlled by MapLibre, not deck.gl.

    **Use `map_options` instead:**

    === "Correct"

        ```python
        MapLibreConfig(
            style=MapLibreStyle.CARTO_POSITRON,
            map_options={
                'dragRotate': False,
                'maxPitch': 0,
                'maxZoom': 16,
            },
        )
        ```

    === "Incorrect (has no effect)"

        ```python
        # These controller settings are silently ignored!
        DeckGL(
            id='map',
            maplibre_config=MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON).to_dict(),
            controller={'dragRotate': False, 'maxPitch': 0},  # IGNORED
            ...
        )
        ```

## Available Preset Styles

| Constant | Provider | Description |
|----------|----------|-------------|
| `MapLibreStyle.CARTO_POSITRON` | CARTO | Light theme |
| `MapLibreStyle.CARTO_DARK_MATTER` | CARTO | Dark theme |
| `MapLibreStyle.CARTO_VOYAGER` | CARTO | Colorful theme |
| `MapLibreStyle.OPENFREEMAP_LIBERTY` | OpenFreeMap | Liberty style |
| `MapLibreStyle.OPENFREEMAP_BRIGHT` | OpenFreeMap | Bright style |
| `MapLibreStyle.OPENFREEMAP_POSITRON` | OpenFreeMap | Positron style |

MapTiler styles are also available (`MAPTILER_STREETS`, `MAPTILER_SATELLITE`, etc.) but require an API key appended to the URL:

```python
style = MapLibreStyle.MAPTILER_STREETS + '?key=YOUR_API_KEY'
```

## Custom Raster Sources

Add XYZ or WMS raster tile sources to the MapLibre basemap:

### XYZ Tiles

```python
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle, RasterSource, RasterLayer

config = MapLibreConfig(
    style=MapLibreStyle.empty(),  # Empty style for raster-only maps
    sources={
        'custom-tiles': RasterSource(
            tiles=['https://tiles.example.com/{z}/{x}/{y}.png'],
            tile_size=256,
        ),
    },
    map_layers=[
        RasterLayer(id='raster-layer', source='custom-tiles'),
    ],
)
```

### WMS

```python
config = MapLibreConfig(
    style=MapLibreStyle.empty(),
    sources={
        'wms': RasterSource.from_wms(
            base_url='https://ows.terrestris.de/osm/service',
            layers='TOPO-WMS',
            tile_size=256,
        ),
    },
    map_layers=[
        RasterLayer(id='wms-layer', source='wms'),
    ],
)
```

`RasterSource.from_wms()` builds the full WMS GetMap URL with `{bbox-epsg-3857}` placeholders automatically.

## Vector Tile Sources

Add custom vector tile sources and style them with MapLibre layers:

```python
from deckgl_dash.maplibre import MapLibreConfig, VectorSource, FillLayer, LineLayer

config = MapLibreConfig(
    style='https://tiles.openfreemap.org/styles/liberty',
    sources={
        'custom': VectorSource(tiles=['https://example.com/{z}/{x}/{y}.pbf']),
    },
    map_layers=[
        FillLayer(
            id='buildings',
            source='custom',
            source_layer='buildings',
            fill_color='#ff0000',
            fill_opacity=0.5,
        ),
        LineLayer(
            id='roads',
            source='custom',
            source_layer='roads',
            line_color='#000000',
            line_width=2,
        ),
    ],
)
```

## Switching Basemap Styles

You can dynamically change the basemap style via a Dash callback by updating the `maplibre_config` prop. The component uses `map.setStyle()` under the hood, so the MapLibre map instance, the deck.gl overlay, all deck.gl layers, and the camera position are all preserved across style changes automatically.

!!! tip "Update the prop, don't recreate the component"
    Target the DeckGL component's `maplibre_config` prop directly. Do **not** recreate the entire `DeckGL(...)` component in the callback — that destroys and rebuilds everything from scratch.

```python
from dash import Dash, html, dcc, callback, Output, Input
from deckgl_dash import DeckGL
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

app = Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(
        id='style-picker',
        options=[
            {'label': 'Positron', 'value': MapLibreStyle.CARTO_POSITRON},
            {'label': 'Dark Matter', 'value': MapLibreStyle.CARTO_DARK_MATTER},
            {'label': 'Voyager', 'value': MapLibreStyle.CARTO_VOYAGER},
        ],
        value=MapLibreStyle.CARTO_POSITRON,
        clearable=False,
    ),
    DeckGL(
        id='map',
        maplibre_config=MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON).to_dict(),
        layers=[...],
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        style={'width': '100%', 'height': '600px'},
    ),
])

@callback(Output('map', 'maplibreConfig'), Input('style-picker', 'value'))
def switch_style(style_url):
    return MapLibreConfig(style=style_url).to_dict()
```

See `examples/maplibre_basemap_switch_demo.py` for a full working example.

## Interleaved Mode

By default, deck.gl layers render **on top** of all MapLibre layers for best performance. Set `interleaved=True` to render deck.gl layers between MapLibre layers (e.g., below labels):

```python
config = MapLibreConfig(
    style=MapLibreStyle.CARTO_POSITRON,
    interleaved=True,  # deck.gl layers can render below MapLibre labels
)
```

!!! warning "Performance impact"
    Interleaved mode reduces pan/zoom performance because deck.gl must synchronize rendering with MapLibre on every frame. Only enable it when you need deck.gl layers to appear between MapLibre layers.

## Full Example

```python
from dash import Dash, html
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer, ScatterplotLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

app = Dash(__name__)

geojson = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [-122.4, 37.8]},
            'properties': {'name': 'San Francisco', 'population': 870000},
        }
    ],
}

app.layout = html.Div([
    DeckGL(
        id='map',
        maplibre_config=MapLibreConfig(
            style=MapLibreStyle.CARTO_POSITRON,
            map_options={'maxPitch': 60, 'maxZoom': 18},
        ).to_dict(),
        layers=[
            GeoJsonLayer(
                id='data',
                data=geojson,
                get_fill_color='#FF5722',
                pickable=True,
                point_type='circle',
                get_point_radius=300,
            ),
        ],
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        enable_events=['click', 'hover'],
        tooltip=True,
        style={'width': '100%', 'height': '100vh'},
    ),
])

if __name__ == '__main__':
    app.run(debug=True)
```
