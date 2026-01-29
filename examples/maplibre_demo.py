"""
Demo of MapLibre GL JS integration with deck.gl.

This example demonstrates:
- Using MapLibre GL JS as the basemap renderer
- deck.gl layers rendered as overlays via MapboxOverlay
- Automatic view state synchronization
"""
from dash import Dash, html, callback, Output, Input
import json

from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer, ScatterplotLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

# Sample GeoJSON data (San Francisco neighborhoods)
SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Mission District", "population": 60000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.428, 37.755], [-122.406, 37.755], [-122.406, 37.765],
                    [-122.428, 37.765], [-122.428, 37.755]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Castro", "population": 20000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.445, 37.755], [-122.428, 37.755], [-122.428, 37.765],
                    [-122.445, 37.765], [-122.445, 37.755]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "SoMa", "population": 45000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.415, 37.770], [-122.395, 37.770], [-122.395, 37.785],
                    [-122.415, 37.785], [-122.415, 37.770]
                ]]
            }
        }
    ]
}

# Sample point data
SAMPLE_POINTS = [
    {"coordinates": [-122.4194, 37.7749], "name": "City Hall", "value": 100},
    {"coordinates": [-122.4089, 37.7855], "name": "Coit Tower", "value": 80},
    {"coordinates": [-122.4175, 37.7620], "name": "Dolores Park", "value": 90},
    {"coordinates": [-122.3894, 37.7864], "name": "Ferry Building", "value": 95},
]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("MapLibre GL JS + deck.gl Integration Demo"),
    html.P("This map uses MapLibre GL JS for the basemap with deck.gl layers as overlays."),
    DeckGL(
        id = 'map',
        # MapLibre configuration - use CARTO Positron basemap
        maplibre_config = MapLibreConfig(
            style = MapLibreStyle.CARTO_POSITRON,
        ).to_dict(),
        # deck.gl layers rendered on top of MapLibre basemap
        layers = [
            GeoJsonLayer(
                id = 'neighborhoods',
                data = SAMPLE_GEOJSON,
                filled = True,
                stroked = True,
                get_fill_color = '#FF5722',
                get_line_color = '#000000',
                get_line_width = 2,
                line_width_min_pixels = 1,
                pickable = True,
                auto_highlight = True,
                highlight_color = [255, 255, 0, 100],
                opacity = 0.5,
            ),
            ScatterplotLayer(
                id = 'points',
                data = SAMPLE_POINTS,
                get_position = '@@=coordinates',
                get_radius = '@@=value',
                get_fill_color = '#2196F3',
                radius_scale = 10,
                radius_min_pixels = 5,
                radius_max_pixels = 50,
                pickable = True,
                auto_highlight = True,
            ),
        ],
        initial_view_state = {
            'longitude': -122.41,
            'latitude': 37.77,
            'zoom': 12,
            'pitch': 0,
            'bearing': 0
        },
        enable_events = ['click', 'hover'],
        tooltip = True,
        style = {'width': '100%', 'height': '600px'},
    ),
    html.Div([
        html.H3("Click Info:"),
        html.Pre(id = 'click-output', style = {'backgroundColor': '#f5f5f5', 'padding': '10px'}),
    ]),
])


@callback(Output('click-output', 'children'), Input('map', 'clickInfo'))
def display_click(click_info):
    if click_info is None:
        return "Click on a feature..."
    return json.dumps(click_info, indent = 2)


if __name__ == '__main__':
    app.run(debug = True, port = 8052)
