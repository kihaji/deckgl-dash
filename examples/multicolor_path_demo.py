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
import math

from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, PathLayer

# A track of (lon, lat, t_seconds) fixes around San Francisco.
# The jump from index 3 -> 4 covers a large distance in a tiny time delta: impossible.
TRACK = [
    (-122.420, 37.770, 0),
    (-122.415, 37.772, 60),
    (-122.410, 37.774, 120),
    (-122.405, 37.776, 180),
    (-122.360, 37.800, 190),   # <-- impossible: ~5 km in 10 s
    (-122.355, 37.802, 250),
    (-122.350, 37.804, 310),
]

# Speed (m/s) above which a segment is flagged "impossible".
IMPOSSIBLE_SPEED_MPS = 100.0  # ~360 km/h
NORMAL_COLOR = [30, 110, 230]    # blue
IMPOSSIBLE_COLOR = [230, 30, 30]  # red


def _haversine_m(lon1, lat1, lon2, lat2):
    """Great-circle distance between two lon/lat points, in meters."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def speeds_to_colors(track):
    """Compute one color per segment from per-segment speed.

    Returns a list of [r, g, b] colors of length len(track) - 1 (one per segment).
    """
    colors = []
    for (lon1, lat1, t1), (lon2, lat2, t2) in zip(track, track[1:]):
        dt = max(t2 - t1, 1e-6)
        speed = _haversine_m(lon1, lat1, lon2, lat2) / dt
        colors.append(IMPOSSIBLE_COLOR if speed > IMPOSSIBLE_SPEED_MPS else NORMAL_COLOR)
    return colors


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
