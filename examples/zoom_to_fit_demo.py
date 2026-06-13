"""
Zoom-to-fit demo (deck-only mode) for deckgl-dash.

The map opens zoomed far out. Clicking "Zoom to fit" frames all scattered features
tightly using the viewport-aware `fitBounds` prop. In deck-only mode (no MapLibre),
the component computes the fit with `WebMercatorViewport.fitBounds` using the map
container's real pixel size — so the result is a tight fit, not an approximation.

Usage:
    python examples/zoom_to_fit_demo.py
"""
import random
from dash import Dash, html, callback, Output, Input

from deckgl_dash import DeckGL, compute_bounds
from deckgl_dash.layers import TileLayer, ScatterplotLayer

# Features scattered across the San Francisco Bay Area.
random.seed(42)
POINTS = [
    {"coordinates": [-122.45 + random.uniform(-0.15, 0.15), 37.75 + random.uniform(-0.12, 0.12)],
     "value": random.randint(20, 100)}
    for _ in range(40)
]

# Far-out starting camera so the "Zoom to fit" effect is obvious.
START_VIEW = {"longitude": -100.0, "latitude": 40.0, "zoom": 3, "pitch": 0, "bearing": 0}

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Zoom to fit (deck-only mode)"),
    html.P("The map starts zoomed out over North America. Click 'Zoom to fit' to tightly "
           "frame the scattered points using the viewport-aware fitBounds prop."),
    html.Div([
        html.Button("Zoom to fit", id="btn-fit", n_clicks=0,
                    style={"padding": "10px 24px", "fontSize": "16px", "cursor": "pointer",
                           "background": "#1976d2", "color": "white", "border": "none", "borderRadius": "4px"}),
        html.Span(id="status", children="", style={"marginLeft": "20px", "color": "#666"}),
    ], style={"marginBottom": "12px"}),
    DeckGL(
        id="map",
        layers=[
            TileLayer(id="osm-tiles", data="https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
                      min_zoom=0, max_zoom=19, tile_size=256),
            ScatterplotLayer(id="points", data=POINTS, get_position="@@=coordinates",
                             get_radius="@@=value", get_fill_color="#e53935",
                             radius_scale=10, radius_min_pixels=4, radius_max_pixels=40,
                             pickable=True, auto_highlight=True),
        ],
        initial_view_state=START_VIEW,
        controller=True,
        enable_events=["click"],
        style={"width": "100%", "height": "600px"},
    ),
])


@callback(
    Output("map", "fitBounds"),
    Output("status", "children"),
    Input("btn-fit", "n_clicks"),
    prevent_initial_call=True,
)
def zoom_to_fit(fit_clicks):
    # `nonce` makes each click a distinct value so Dash re-sends the prop (and the
    # React effect re-fires) even though the bounds are identical between clicks.
    fit = {"bounds": compute_bounds(POINTS), "padding": 40, "maxZoom": 16, "nonce": fit_clicks}
    return fit, f"Fitted {len(POINTS)} points."


if __name__ == "__main__":
    app.run(debug=True, port=8054)
