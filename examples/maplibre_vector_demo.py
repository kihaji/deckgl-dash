"""
Demo of vector tile (PBF) styling with MapLibre GL JS.

This example demonstrates:
- Using a pre-styled MapLibre basemap
- Adding custom MapLibre layers for vector tile styling
- Combining MapLibre vector styling with deck.gl layers
"""
from dash import Dash, html, callback, Output, Input
import json

from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

# Sample GeoJSON overlay data
SAMPLE_OVERLAY = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "San Francisco Bay Area", "type": "region"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.6, 37.4], [-122.0, 37.4], [-122.0, 37.9],
                    [-122.6, 37.9], [-122.6, 37.4]
                ]]
            }
        },
    ]
}

app = Dash(__name__)

app.layout = html.Div([
    html.H1("MapLibre Vector Tile Demo"),
    html.P("This map uses OpenFreeMap (vector tiles) with deck.gl overlay."),
    html.Div([
        html.Label("Select basemap style:"),
        html.Select(
            id = 'style-selector',
            children = [
                html.Option(value = 'liberty', children = 'Liberty (Default)'),
                html.Option(value = 'bright', children = 'Bright'),
                html.Option(value = 'positron', children = 'Positron'),
                html.Option(value = 'carto-dark', children = 'CARTO Dark Matter'),
                html.Option(value = 'carto-voyager', children = 'CARTO Voyager'),
            ],
            style = {'marginLeft': '10px', 'padding': '5px'},
        ),
    ], style = {'marginBottom': '10px'}),
    html.Div(id = 'map-container'),
    html.Div([
        html.H4("About Vector Tiles"),
        html.P([
            "Vector tiles (PBF format) provide high-quality, scalable maps with full styling control. ",
            "This demo uses ",
            html.A("OpenFreeMap", href = "https://openfreemap.org/"),
            " which provides free vector tile styles based on OpenStreetMap data."
        ]),
    ], style = {'padding': '20px'}),
])


@callback(Output('map-container', 'children'), Input('style-selector', 'value'))
def update_map(style_value):
    # Map style selector value to actual style URL
    style_map = {
        'liberty': MapLibreStyle.OPENFREEMAP_LIBERTY,
        'bright': MapLibreStyle.OPENFREEMAP_BRIGHT,
        'positron': MapLibreStyle.OPENFREEMAP_POSITRON,
        'carto-dark': MapLibreStyle.CARTO_DARK_MATTER,
        'carto-voyager': MapLibreStyle.CARTO_VOYAGER,
    }
    style_url = style_map.get(style_value, MapLibreStyle.OPENFREEMAP_LIBERTY)

    return DeckGL(
        id = 'map',
        maplibre_config = MapLibreConfig(style = style_url).to_dict(),
        layers = [
            GeoJsonLayer(
                id = 'overlay',
                data = SAMPLE_OVERLAY,
                filled = True,
                stroked = True,
                get_fill_color = [255, 87, 34, 50],  # Semi-transparent orange
                get_line_color = '#FF5722',
                get_line_width = 3,
                line_width_min_pixels = 2,
                pickable = True,
            ),
        ],
        initial_view_state = {
            'longitude': -122.3,
            'latitude': 37.65,
            'zoom': 9,
            'pitch': 0,
            'bearing': 0
        },
        enable_events = ['click'],
        tooltip = True,
        style = {'width': '100%', 'height': '600px'},
    )


if __name__ == '__main__':
    app.run(debug = True, port = 8054)
