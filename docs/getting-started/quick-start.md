# Quick Start

deckgl-dash supports two usage modes: **Python helper classes** (recommended) and **raw JSON dicts**. Both produce the same result.

## Your First Map

=== "Python Helpers"

    ```python
    from dash import Dash, html
    from deckgl_dash import DeckGL
    from deckgl_dash.layers import TileLayer, GeoJsonLayer

    app = Dash(__name__)

    geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [-122.4, 37.8]},
                'properties': {'name': 'San Francisco'},
            }
        ],
    }

    app.layout = html.Div([
        DeckGL(
            id='map',
            layers=[
                TileLayer(
                    id='basemap',
                    data='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    min_zoom=0,
                    max_zoom=19,
                ),
                GeoJsonLayer(
                    id='data',
                    data=geojson,
                    get_fill_color='#FF8C00',
                    get_line_color='#000000',
                    pickable=True,
                    point_type='circle',
                    get_point_radius=500,
                ),
            ],
            initial_view_state={
                'longitude': -122.4,
                'latitude': 37.8,
                'zoom': 11,
                'pitch': 0,
                'bearing': 0,
            },
            tooltip=True,
            style={'width': '100%', 'height': '100vh'},
        )
    ])

    if __name__ == '__main__':
        app.run(debug=True)
    ```

=== "JSON Dicts"

    ```python
    from dash import Dash, html
    from deckgl_dash import DeckGL

    app = Dash(__name__)

    geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [-122.4, 37.8]},
                'properties': {'name': 'San Francisco'},
            }
        ],
    }

    app.layout = html.Div([
        DeckGL(
            id='map',
            layers=[
                {
                    '@@type': 'TileLayer',
                    'id': 'basemap',
                    'data': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    'minZoom': 0,
                    'maxZoom': 19,
                },
                {
                    '@@type': 'GeoJsonLayer',
                    'id': 'data',
                    'data': geojson,
                    'getFillColor': [255, 140, 0],
                    'getLineColor': [0, 0, 0],
                    'pickable': True,
                    'pointType': 'circle',
                    'getPointRadius': 500,
                },
            ],
            initialViewState={
                'longitude': -122.4,
                'latitude': 37.8,
                'zoom': 11,
                'pitch': 0,
                'bearing': 0,
            },
            tooltip=True,
            style={'width': '100%', 'height': '100vh'},
        )
    ])

    if __name__ == '__main__':
        app.run(debug=True)
    ```

## Understanding the Code

| Prop | Purpose |
|------|---------|
| `id` | Unique component ID for Dash callbacks |
| `layers` | List of deck.gl layers (Python helpers or JSON dicts) |
| `initial_view_state` | Camera position: longitude, latitude, zoom, pitch, bearing |
| `tooltip` | `True` shows all properties on hover; can also be a dict for custom templates |
| `style` | CSS style dict for the map container |

## Enabling Click & Hover Events

Events are **disabled by default** for performance. Enable them to use Dash callbacks:

```python
from dash import Dash, html, Output, Input
from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, GeoJsonLayer

app = Dash(__name__)

app.layout = html.Div([
    DeckGL(
        id='map',
        layers=[
            TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
            GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True),
        ],
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        enable_events=['click', 'hover'],  # Enable specific events
    ),
    html.Div(id='click-output'),
])


@app.callback(
    Output('click-output', 'children'),
    Input('map', 'clickInfo'),
)
def display_click(click_info):
    if click_info is None:
        return 'Click a feature on the map'
    return f"Clicked: {click_info}"
```

!!! warning "Events must be explicitly enabled"
    If `click_info` or `hover_info` never updates in your callback, check that you've set `enable_events`. See [Gotchas](../troubleshooting/gotchas.md) for more.

## Updating Layer Data

Use the `layer_data` prop to update individual layer data without resending the entire `layers` array:

```python
from dash import Dash, html, Output, Input, callback
from deckgl_dash import DeckGL
from deckgl_dash.layers import HexagonLayer, ScatterplotLayer, process_layers

app = Dash(__name__)

app.layout = html.Div([
    html.Button("Load Data", id="load-btn"),
    DeckGL(
        id='map',
        layers=process_layers([
            HexagonLayer(id='hexagons', data=[], get_position='@@=coordinates', radius=100),
            ScatterplotLayer(id='scatter', data=STATIC_POINTS, get_position='@@=coordinates'),
        ]),
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
    ),
])


@callback(Output('map', 'layerData'), Input('load-btn', 'n_clicks'), prevent_initial_call=True)
def load_hexagons(n):
    return {'hexagons': generate_points()}  # only hexagon data is serialized
```

The ScatterplotLayer data is never re-serialized. See the [Layer Data Updates Guide](../guides/layer-data-updates.md) for more patterns.

## Using MapLibre Basemaps

For vector tile basemaps instead of raster tiles, use the MapLibre integration:

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

See the [MapLibre Integration Guide](../guides/maplibre-integration.md) for details.
