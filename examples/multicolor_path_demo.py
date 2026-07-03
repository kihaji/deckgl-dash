"""
Demo of per-segment Path coloring (MultiColorPathLayer).

deck.gl's stock PathLayer paints one color per whole path. This demo uses the
``multi_color=True`` flag on the PathLayer helper, which serializes the layer as
``@@type: "MultiColorPathLayer"`` and lets ``get_color`` return a list of colors,
one per segment.

Scenario: a GPS track where each segment is colored by speed. Most of the track is
"normal" (blue), but one segment is an "impossible journey" — the object covers far
too much distance for the elapsed time (e.g. a spoofed/teleported fix) — and is drawn
in red. The whole track remains a single pickable/hoverable object.
"""
from dash import Dash, html, callback, Output, Input
import json

from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, PathLayer

from _common import TRACK, speeds_to_colors

# Build a single track feature: one path, one color-per-segment list.
TRACK_DATA = [{
    'name': 'Asset Alpha',
    'path': [[lon, lat] for lon, lat, _ in TRACK],
    'segmentColors': speeds_to_colors(TRACK),
}]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Per-segment Path coloring (MultiColorPathLayer)"),
    html.P("Most of the track is blue; the one 'impossible' segment (too fast for the "
           "elapsed time) is red. Click or hover the track — it is a single object."),
    DeckGL(
        id = 'map',
        layers = [
            TileLayer(
                id = 'osm-tiles',
                data = 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                min_zoom = 0,
                max_zoom = 19,
                tile_size = 256,
            ),
            PathLayer(
                id = 'track',
                data = TRACK_DATA,
                get_path = '@@=path',
                get_color = '@@=segmentColors',   # list of [r,g,b] per segment
                multi_color = True,               # -> @@type: MultiColorPathLayer
                get_width = 6,
                width_min_pixels = 4,
                cap_rounded = True,
                joint_rounded = True,
                pickable = True,
                auto_highlight = True,
            ),
        ],
        initial_view_state = {
            'longitude': -122.39,
            'latitude': 37.785,
            'zoom': 12,
            'pitch': 0,
            'bearing': 0,
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
])


@callback(Output('click-output', 'children'), Input('map', 'clickInfo'))
def display_click(click_info):
    if click_info is None:
        return "Click the track..."
    return json.dumps(click_info, indent = 2)


if __name__ == '__main__':
    app.run(debug = True, port = 8052)
