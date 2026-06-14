"""
Directed paths (arrows) + time slider demo for deckgl-dash.

A set of trips, each a short ordered track with direction-of-travel arrows
(DirectedPathLayer, `show_direction=True`) and a start time `t`. A sliding time window
`[T - window, T]` selects which trips are visible, filtered on the GPU via
DataFilterExtension — the line AND its arrows fade in/out together. Press Play to sweep
the window across the day at 60fps with no per-frame server round trips; the throttled
`currentTime` drives the slider handle and readout. Pause and drag to scrub.

Each trip is colored by its start time (early = blue, late = red), so playback reads as
a wave of activity moving through time.

Usage:
    python examples/path_arrows_time_slider_demo.py
"""
import random
from dash import Dash, dcc, html, callback, Output, Input, State, ctx, no_update

from deckgl_dash import DeckGL, compute_bounds, compute_time_domain, build_time_filter
from deckgl_dash.layers import TileLayer, PathLayer

# Total time span of the dataset, in seconds (small => float32-safe filter values).
DURATION_S = 600.0


def _lerp_color(frac):
    """Blue (early) -> red (late) ramp; frac in [0, 1] -> [r, g, b]."""
    frac = max(0.0, min(1.0, frac))
    return [int(40 + 200 * frac), int(60 + 40 * (1 - frac)), int(220 - 180 * frac)]


def make_trips(n=60, seed=7):
    """Build n trips, each an ordered random-walk path with a start time `t` and color.

    Pure and deterministic so it can be unit-tested. `t` is seconds since the start.
    """
    rng = random.Random(seed)
    trips = []
    for _ in range(n):
        lng = -122.44 + rng.uniform(-0.12, 0.12)
        lat = 37.76 + rng.uniform(-0.10, 0.10)
        # A short ordered walk (points are time-ordered, so arrows show direction).
        path = [[lng, lat]]
        for _ in range(rng.randint(4, 7)):
            lng += rng.uniform(-0.02, 0.02)
            lat += rng.uniform(-0.016, 0.016)
            path.append([lng, lat])
        t = rng.uniform(0.0, DURATION_S)
        trips.append({"path": path, "t": t, "color": _lerp_color(t / DURATION_S)})
    return trips


TRIPS = make_trips()
DOMAIN = compute_time_domain(TRIPS, "t")           # [t_min, t_max]
WINDOW = (DOMAIN[1] - DOMAIN[0]) * 0.15            # show a 15%-wide trailing window
FIT = {"bounds": compute_bounds(TRIPS), "padding": 50, "maxZoom": 13}

SPAN = DOMAIN[1] - DOMAIN[0]
SPEEDS = {"0.5x": SPAN / 40.0, "1x": SPAN / 20.0, "2x": SPAN / 10.0, "4x": SPAN / 5.0}

INITIAL_TF = build_time_filter(DOMAIN, WINDOW, speed=SPEEDS["1x"])


def fmt(t):
    return f"t = {t:6.1f} s   (window {WINDOW:.0f} s)"


app = Dash(__name__)

_btn = {"padding": "8px 18px", "fontSize": "15px", "cursor": "pointer", "border": "none",
        "borderRadius": "4px", "color": "white", "marginRight": "8px"}

app.layout = html.Div([
    html.H1("Directed paths (arrows) + time slider"),
    html.P("Each trip shows its direction of travel with arrows. The sliding time window "
           "filters whole trips on the GPU — line and arrows fade together. Press Play to "
           "sweep the day; pause and drag to scrub. Trips are colored by start time "
           "(blue = early, red = late)."),
    html.Div([
        html.Button("▶ Play", id="btn-play", n_clicks=0, style={**_btn, "background": "#2e7d32"}),
        html.Button("⏸ Pause", id="btn-pause", n_clicks=0, style={**_btn, "background": "#c62828"}),
        html.Span("Speed:", style={"margin": "0 8px 0 16px"}),
        dcc.Dropdown(id="speed", options=list(SPEEDS.keys()), value="1x", clearable=False,
                     style={"width": "100px", "display": "inline-block", "verticalAlign": "middle"}),
        html.Span(id="time-readout", children=fmt(INITIAL_TF["current"]),
                  style={"marginLeft": "20px", "color": "#444", "fontFamily": "monospace"}),
    ], style={"marginBottom": "10px", "display": "flex", "alignItems": "center"}),
    dcc.Slider(id="time-slider", min=DOMAIN[0], max=DOMAIN[1], value=INITIAL_TF["current"],
               step=(SPAN / 500.0), marks=None, tooltip={"placement": "bottom"},
               updatemode="drag"),
    DeckGL(
        id="map",
        layers=[
            TileLayer(id="osm-tiles", data="https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
                      min_zoom=0, max_zoom=19, tile_size=256),
            PathLayer(id="trips", data=TRIPS, get_path="@@=path", get_color="@@=color",
                      get_filter_value="@@=t",  # auto-attaches DataFilterExtension
                      show_direction=True, arrow_spacing=55, arrow_size=20,
                      get_width=5, width_min_pixels=3, cap_rounded=True, joint_rounded=True,
                      pickable=True, auto_highlight=True),
        ],
        initial_view_state={"longitude": -122.44, "latitude": 37.76, "zoom": 10},
        fit_bounds=FIT,
        time_filter=INITIAL_TF,
        enable_events=["click"],
        controller=True,
        style={"width": "100%", "height": "600px"},
    ),
])


@callback(
    Output("map", "timeFilter"),
    Output("time-slider", "value"),
    Output("time-readout", "children"),
    Input("btn-play", "n_clicks"),
    Input("btn-pause", "n_clicks"),
    Input("speed", "value"),
    Input("time-slider", "value"),
    Input("map", "currentTime"),
    State("map", "timeFilter"),
    prevent_initial_call=True,
)
def control(_play, _pause, speed_key, slider_value, current_time, tf):
    """Single owner of timeFilter + slider + readout (see time_slider_demo for the loop guard)."""
    tf = dict(tf or INITIAL_TF)
    trig = ctx.triggered_id

    if trig == "map":  # playback tick: advance the handle + readout only
        if current_time is None:
            return no_update, no_update, no_update
        return no_update, current_time, fmt(current_time)

    if trig == "btn-play":
        tf["playing"] = True
        return tf, no_update, no_update

    if trig == "btn-pause":
        tf["playing"] = False
        return tf, no_update, no_update

    if trig == "speed":
        tf["speed"] = SPEEDS[speed_key]
        return tf, no_update, no_update

    if trig == "time-slider":
        if tf.get("playing"):  # programmatic echo during playback — ignore
            return no_update, no_update, no_update
        tf["current"] = slider_value
        tf["nonce"] = (tf.get("nonce") or 0) + 1
        return tf, no_update, fmt(slider_value)

    return no_update, no_update, no_update


if __name__ == "__main__":
    app.run(debug=True, port=8056)
