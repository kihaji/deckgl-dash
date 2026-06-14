"""
Time-slider + animation demo for deckgl-dash.

A field of points each carry an appearance time `t`. A sliding time window
`[T - window, T]` selects which points are visible, filtered on the GPU via deck.gl's
DataFilterExtension. Pressing Play animates the head T across the full time domain at
60fps with no per-frame server round trips — only the throttled `currentTime` is reported
back, which drives the slider handle and the readout.

Drag the slider (while paused) to scrub to any moment. Filtering happens entirely
client-side; Dash only sets up the animation and reads the current time.

Float32 note: `t` is kept small (seconds since the domain start) so it stays within
float32 precision used by DataFilterExtension. See `deckgl_dash.timefilter`.

Usage:
    python examples/time_slider_demo.py
"""
import random
from dash import Dash, dcc, html, callback, Output, Input, State, ctx, no_update

from deckgl_dash import DeckGL, compute_bounds, compute_time_domain, build_time_filter
from deckgl_dash.layers import TileLayer, ScatterplotLayer

# Total time span of the dataset, in seconds (small => float32-safe filter values).
DURATION_S = 600.0


def make_points(n=4000, seed=42):
    """Build n points scattered over the SF Bay Area, each with an appearance time `t`.

    Pure and deterministic so it can be unit-tested. `t` is seconds since the start.
    """
    rng = random.Random(seed)
    points = []
    for _ in range(n):
        points.append({
            "coordinates": [-122.44 + rng.uniform(-0.18, 0.18), 37.76 + rng.uniform(-0.14, 0.14)],
            "t": rng.uniform(0.0, DURATION_S),
            "value": rng.randint(20, 100),
        })
    return points


POINTS = make_points()
DOMAIN = compute_time_domain(POINTS, "t")          # [t_min, t_max]
WINDOW = (DOMAIN[1] - DOMAIN[0]) * 0.1             # show a 10%-wide trailing window
FIT = {"bounds": compute_bounds(POINTS), "padding": 40, "maxZoom": 14}

# Speed presets: full sweeps of the domain in N seconds of wall-clock time.
SPAN = DOMAIN[1] - DOMAIN[0]
SPEEDS = {"0.5x": SPAN / 40.0, "1x": SPAN / 20.0, "2x": SPAN / 10.0, "4x": SPAN / 5.0}

INITIAL_TF = build_time_filter(DOMAIN, WINDOW, speed=SPEEDS["1x"])


def fmt(t):
    return f"t = {t:6.1f} s   (window {WINDOW:.0f} s)"


app = Dash(__name__)

_btn = {"padding": "8px 18px", "fontSize": "15px", "cursor": "pointer", "border": "none",
        "borderRadius": "4px", "color": "white", "marginRight": "8px"}

app.layout = html.Div([
    html.H1("Time slider + animation"),
    html.P("Press Play to animate the sliding time window on the GPU (60fps, no server "
           "round trips). Pause and drag the slider to scrub to any moment."),
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
            ScatterplotLayer(id="points", data=POINTS, get_position="@@=coordinates",
                             get_filter_value="@@=t",  # auto-attaches DataFilterExtension
                             get_radius="@@=value", get_fill_color="#1565c0",
                             radius_scale=6, radius_min_pixels=2, radius_max_pixels=18,
                             opacity=0.8),
        ],
        initial_view_state={"longitude": -122.44, "latitude": 37.76, "zoom": 9},
        fit_bounds=FIT,
        time_filter=INITIAL_TF,
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
    """Single owner of timeFilter + slider + readout, dispatched by trigger.

    Loop guard: during playback the engine pushes `currentTime`, which we echo to the
    slider handle. That echo re-fires this callback with trigger "time-slider"; because
    `tf["playing"]` is True we ignore it, so the slider never fights the animation.
    Genuine scrubbing only happens while paused.
    """
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
        tf["nonce"] = (tf.get("nonce") or 0) + 1  # force re-sync of an unchanged value
        return tf, no_update, fmt(slider_value)

    return no_update, no_update, no_update


if __name__ == "__main__":
    app.run(debug=True, port=8055)
