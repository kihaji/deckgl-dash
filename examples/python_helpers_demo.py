"""
Demo of dash-deckgl Python layer helpers.

This example demonstrates:
- Using Python layer classes instead of JSON/dict
- Hex color strings (#FF8C00)
- Accessor strings (@@=property.path)
- Click events with pickable layers
"""
from dash import Dash, html, callback, Output, Input
import json

from dash_deckgl import DeckGL
from dash_deckgl.layers import TileLayer, GeoJsonLayer, ScatterplotLayer

# Sample GeoJSON data (San Francisco neighborhoods)
SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Mission District", "population": 60000, "color": [255, 100, 100]},
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
            "properties": {"name": "Castro", "population": 20000, "color": [100, 100, 255]},
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
            "properties": {"name": "SoMa", "population": 45000, "color": [100, 255, 100]},
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
    html.H1("dash-deckgl Python Layer Helpers Demo"),
    html.P("Click on a polygon or point to see its properties."),
    DeckGL(
        id = 'map',
        layers = [
            # Base map using Python helper with snake_case props
            TileLayer(
                id = 'osm-tiles',
                data = 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                min_zoom = 0,
                max_zoom = 19,
                tile_size = 256,
            ),
            # GeoJSON layer with hex colors and accessor strings
            GeoJsonLayer(
                id = 'neighborhoods',
                data = SAMPLE_GEOJSON,
                filled = True,
                stroked = True,
                # Use accessor string to get color from feature properties
                get_fill_color = '@@=properties.color',
                get_line_color = '#000000',  # Hex color support
                get_line_width = 2,
                line_width_min_pixels = 1,
                pickable = True,
                auto_highlight = True,
                highlight_color = [255, 255, 0, 100],
                opacity = 0.6,
            ),
            # Scatterplot layer for points
            ScatterplotLayer(
                id = 'points',
                data = SAMPLE_POINTS,
                get_position = '@@=coordinates',
                get_radius = '@@=value',  # Data-driven radius
                get_fill_color = '#FF5722',  # Hex color
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
        controller = True,
        enable_events = ['click', 'hover'],
        tooltip = True,
        style = {'width': '100%', 'height': '600px'},
    ),
    html.Div([
        html.H3("Click Info:"),
        html.Pre(id = 'click-output', style = {'backgroundColor': '#f5f5f5', 'padding': '10px'}),
    ]),
    html.Div([
        html.H3("Hover Info:"),
        html.Pre(id = 'hover-output', style = {'backgroundColor': '#f5f5f5', 'padding': '10px'}),
    ]),
])


@callback(Output('click-output', 'children'), Input('map', 'clickInfo'))
def display_click(click_info):
    if click_info is None:
        return "Click on a feature..."
    return json.dumps(click_info, indent = 2)


@callback(Output('hover-output', 'children'), Input('map', 'hoverInfo'))
def display_hover(hover_info):
    if hover_info is None or not hover_info.get('picked'):
        return "Hover over a feature..."
    return json.dumps(hover_info, indent = 2)


if __name__ == '__main__':
    app.run(debug = True, port = 8051)
