"""
Demo of custom raster tile source with MapLibre GL JS.

This example demonstrates:
- Adding custom raster tile sources to MapLibre
- MapLibre raster layer styling
- Combining raster basemap with deck.gl overlays
"""
from dash import Dash, html

from deckgl_dash import DeckGL
from deckgl_dash.layers import ScatterplotLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle, RasterSource, RasterLayer

# Sample point data - locations around the world
LOCATIONS = [
    {"coordinates": [-122.4194, 37.7749], "name": "San Francisco", "temp": 15},
    {"coordinates": [-118.2437, 34.0522], "name": "Los Angeles", "temp": 22},
    {"coordinates": [-73.9857, 40.7484], "name": "New York", "temp": 10},
    {"coordinates": [139.6917, 35.6895], "name": "Tokyo", "temp": 18},
    {"coordinates": [-43.1729, -22.9068], "name": "Rio de Janeiro", "temp": 28},
    {"coordinates": [151.2093, -33.8688], "name": "Sydney", "temp": 25},
]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("MapLibre Custom Raster Source Demo"),
    html.P("This map uses Stadia Stamen Watercolor tiles as a custom raster source."),
    DeckGL(
        id = 'map',
        maplibre_config = MapLibreConfig(
            # Start with empty style since raster source provides the basemap
            style = MapLibreStyle.empty(),
            # Add custom raster tile source - Stadia Stamen Watercolor (free, no API key for low volume)
            sources = {
                'stamen-watercolor': RasterSource(
                    tiles = ['https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg'],
                    tile_size = 256,
                    attribution = '&copy; <a href="https://stamen.com">Stamen Design</a>',
                ),
            },
            # Add raster layer to display the tiles
            map_layers = [
                RasterLayer(
                    id = 'watercolor-layer',
                    source = 'stamen-watercolor',
                    raster_opacity = 1.0,
                ),
            ],
        ).to_dict(),
        # deck.gl layer on top of raster basemap
        layers = [
            ScatterplotLayer(
                id = 'locations',
                data = LOCATIONS,
                get_position = '@@=coordinates',
                get_radius = 500000,
                get_fill_color = '#D32F2F',
                radius_min_pixels = 10,
                radius_max_pixels = 50,
                pickable = True,
                opacity = 0.9,
            ),
        ],
        initial_view_state = {
            'longitude': 0,
            'latitude': 20,
            'zoom': 2,
            'pitch': 0,
            'bearing': 0
        },
        enable_events = ['hover'],
        tooltip = {'html': '<b>{name}</b><br>Temp: {temp}°C'},
        style = {'width': '100%', 'height': '600px'},
    ),
    html.Div([
        html.H4("About this demo"),
        html.P([
            "The basemap uses custom raster tiles from ",
            html.A("Stadia Maps", href = "https://stadiamaps.com/"),
            " (Stamen Watercolor style). This demonstrates adding custom tile sources ",
            "to MapLibre with deck.gl overlays on top."
        ]),
    ], style = {'padding': '20px'}),
])


if __name__ == '__main__':
    app.run(debug = True, port = 8053)
