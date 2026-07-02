"""
Basic usage example for deckgl-dash with OpenStreetMap TileLayer
"""
from dash import Dash, html, callback, Output, Input
from deckgl_dash import DeckGL

app = Dash(__name__)

app.layout = html.Div([
    html.H1("deckgl-dash Demo"),
    DeckGL(
        id = 'map',
        layers = [
            {
                '@@type': 'TileLayer',
                'id': 'osm-tiles',
                'data': 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'minZoom': 0,
                'maxZoom': 19,
                'tileSize': 256,
            }
        ],
        initialViewState = {
            'longitude': -122.4,
            'latitude': 37.8,
            'zoom': 11,
            'pitch': 0,
            'bearing': 0
        },
        controller = True,
        style = {'width': '100%', 'height': '600px'},
    ),
    html.Div(id = 'output')
])


if __name__ == '__main__':
    app.run(debug = True)
