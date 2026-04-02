"""
Demo of coordinate conversion on map click.

This example demonstrates:
- Clicking anywhere on the map to get coordinates
- Converting coordinates to DD, DMS, UTM, and MGRS formats
- Using CoordinateConverter.from_click_info() in a Dash callback

Requires optional dependencies: pip install pyproj mgrs
"""
from dash import Dash, html, callback, Output, Input

from deckgl_dash import DeckGL, CoordinateConverter
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Click anywhere on the map to see coordinates"),
    html.Div([
        DeckGL(
            id = 'map',
            layers = [
                TileLayer(
                    id = 'basemap',
                    data = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    min_zoom = 0, max_zoom = 19,
                    tile_size = 256,
                ),
            ],
            initial_view_state = {'longitude': -98.5795, 'latitude': 39.8283, 'zoom': 4, 'pitch': 0, 'bearing': 0},
            enable_events = ['click'],
            style = {'width': '100%', 'height': '600px'},
        ),
    ]),
    html.Div(id = 'coord-output', style = {'marginTop': '20px', 'fontFamily': 'monospace', 'fontSize': '14px'}),
])


@callback(Output('coord-output', 'children'), Input('map', 'clickInfo'))
def display_coordinates(click_info):
    if not click_info or not click_info.get('coordinate'):
        return "Click on the map to see coordinates..."

    coord = CoordinateConverter.from_click_info(click_info)

    rows: list[html.Div | html.Hr] = [
        html.Div(f"Decimal Degrees:  {coord.dd}"),
        html.Div(f"DMS:              {coord.dms}"),
    ]

    try:
        rows.append(html.Div(f"UTM:              {coord.utm}"))
    except ImportError:
        rows.append(html.Div("UTM:              (install pyproj for UTM support)"))

    try:
        rows.append(html.Div(f"MGRS:             {coord.mgrs}"))
    except ImportError:
        rows.append(html.Div("MGRS:             (install mgrs for MGRS support)"))

    if click_info.get('picked'):
        rows.append(html.Hr())
        rows.append(html.Div(f"Picked layer: {click_info.get('layerId')}"))

    return rows


if __name__ == '__main__':
    app.run(debug = True)
