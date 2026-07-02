"""
Direction-of-movement demo (DirectedPathLayer).

For pattern-of-life / track analysis the path points are ordered (here, by time).
Setting ``show_direction=True`` on the PathLayer overlays evenly-spaced arrowheads
that point in the direction of travel, so the order reads at a glance. Combined with
``multi_color=True`` the track shows BOTH speed (per-segment color) and direction
(arrows) — and it's still a single layer / single pickable object.

Arrows are spaced in screen pixels, so they stay evenly spaced and the same size as
you zoom; pan/zoom the map to see them re-flow.

Usage:
    python examples/directed_path_demo.py
"""
from dash import Dash, html, callback, Output, Input
import json

from deckgl_dash import DeckGL, compute_bounds
from deckgl_dash.layers import TileLayer, PathLayer

from _common import TRACK, speeds_to_colors

TRACK_DATA = [{
    'name': 'Asset Alpha',
    'path': [[lon, lat] for lon, lat, _ in TRACK],
    'segmentColors': speeds_to_colors(TRACK),
}]

FIT = {'bounds': compute_bounds(TRACK_DATA), 'padding': 60, 'maxZoom': 14}

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Direction of movement (DirectedPathLayer)"),
    html.P("Arrows point in the direction of travel along the ordered track; segment color "
           "still encodes speed (red = impossible). One layer, one pickable object. "
           "Zoom/pan — arrows stay evenly spaced."),
    DeckGL(
        id='map',
        layers=[
            TileLayer(id='osm-tiles', data='https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                      min_zoom=0, max_zoom=19, tile_size=256),
            PathLayer(
                id='track',
                data=TRACK_DATA,
                get_path='@@=path',
                get_color='@@=segmentColors',
                multi_color=True,        # per-segment speed color
                show_direction=True,     # -> DirectedPathLayer composite (line + arrows)
                arrow_spacing=70,        # pixels between arrows
                arrow_size=22,
                get_width=6,
                width_min_pixels=4,
                cap_rounded=True,
                joint_rounded=True,
                pickable=True,
                auto_highlight=True,
            ),
        ],
        initial_view_state={'longitude': -122.40, 'latitude': 37.785, 'zoom': 12, 'pitch': 0, 'bearing': 0},
        fit_bounds=FIT,
        controller=True,
        enable_events=['click'],
        tooltip=True,
        style={'width': '100%', 'height': '600px'},
    ),
    html.Div([
        html.H3("Click Info:"),
        html.Pre(id='click-output', style={'backgroundColor': '#f5f5f5', 'padding': '10px'}),
    ]),
])


@callback(Output('click-output', 'children'), Input('map', 'clickInfo'))
def display_click(click_info):
    if click_info is None:
        return "Click the track..."
    return json.dumps(click_info, indent=2)


if __name__ == '__main__':
    app.run(debug=True, port=8055)
