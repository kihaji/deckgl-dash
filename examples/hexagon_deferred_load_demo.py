"""
Deferred HexagonLayer data loading demo for deckgl-dash.

Demonstrates initializing a DeckGL map with an empty HexagonLayer, then
loading data into it via the `layer_data` prop. Only the targeted layer's
data is serialized and sent over the wire — the ScatterplotLayer is never
re-serialized.

Usage:
    python examples/hexagon_deferred_load_demo.py
"""
import random
from dash import Dash, html, callback, Output, Input, ctx, no_update
from deckgl_dash import DeckGL, color_range_from_scale
from deckgl_dash.layers import HexagonLayer, ScatterplotLayer, process_layers
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

# Center point (Atlanta, GA area)
CENTER_LON, CENTER_LAT = -83.62, 32.84
NUM_POINTS = 50_000
COLOR_RANGE = color_range_from_scale('viridis', 6)

# Sample points of interest (static, always visible on the map)
SAMPLE_POINTS = [
    {"coordinates": [-83.6300, 32.8450], "name": "Town Center", "value": 100},
    {"coordinates": [-83.6100, 32.8350], "name": "East Park", "value": 80},
    {"coordinates": [-83.6400, 32.8300], "name": "West Station", "value": 90},
    {"coordinates": [-83.6150, 32.8500], "name": "North Mall", "value": 95},
]


def generate_random_points(count: int, center_lat: float, center_lon: float, radius: float = 0.15) -> list:
    """Generate random point data for HexagonLayer aggregation."""
    return [
        {"coordinates": [center_lon + random.uniform(-radius, radius), center_lat + random.uniform(-radius, radius)], "value": random.randint(1, 100)}
        for _ in range(count)
    ]


app = Dash(__name__)

app.layout = html.Div([
    html.H1("HexagonLayer Deferred Load Demo"),
    html.P("The map starts with an empty HexagonLayer. Click the button to load data. "
           "Only the hexagon data is sent — the ScatterplotLayer is never re-serialized."),

    html.Div([
        html.Button("Load Data", id = "btn-load", n_clicks = 0,
                     style = {"padding": "10px 24px", "fontSize": "16px", "cursor": "pointer",
                              "backgroundColor": "#4CAF50", "color": "white", "border": "none", "borderRadius": "4px"}),
        html.Button("Clear Data", id = "btn-clear", n_clicks = 0,
                     style = {"padding": "10px 24px", "fontSize": "16px", "cursor": "pointer", "marginLeft": "10px",
                              "backgroundColor": "#f44336", "color": "white", "border": "none", "borderRadius": "4px"}),
        html.Span(id = "status", children = "No data loaded.",
                  style = {"marginLeft": "20px", "fontSize": "14px", "color": "#666"}),
    ], style = {"marginBottom": "15px", "padding": "10px", "backgroundColor": "#f5f5f5", "borderRadius": "5px"}),

    DeckGL(
        id = "map",
        maplibre_config = MapLibreConfig(
            style = MapLibreStyle.CARTO_POSITRON,
            map_options = {"dragRotate": False, "touchRotate": False, "keyboard": False, "maxPitch": 0},
        ).to_dict(),
        layers = process_layers([
            HexagonLayer(
                id = "hexagons",
                data = [],
                get_position = "@@=coordinates",
                radius = 100,
                color_range = COLOR_RANGE,
                color_aggregation = "SUM",
                extruded = False,
                pickable = False,
                opacity = 0.6,
            ),
            ScatterplotLayer(
                id = "points",
                data = SAMPLE_POINTS,
                get_position = "@@=coordinates",
                get_radius = "@@=value",
                get_fill_color = "#2196F3",
                radius_scale = 10,
                radius_min_pixels = 5,
                radius_max_pixels = 50,
                pickable = True,
                auto_highlight = True,
            ),
        ]),
        initial_view_state = {"longitude": CENTER_LON, "latitude": CENTER_LAT, "zoom": 12, "pitch": 0, "bearing": 0},
        enable_events = ["click"],
        tooltip = {"layers": {"hexagons": {"html": "<b>Point Count:</b> {colorValue}"}}, "default": {"html": "Hover for info"}},
        style = {"width": "100%", "height": "700px"},
    ),
], style = {"padding": "20px", "fontFamily": "sans-serif"})


@callback(
    Output("map", "layerData"),
    Output("status", "children"),
    Input("btn-load", "n_clicks"),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call = True,
)
def update_data(load_clicks, clear_clicks):
    """Load or clear HexagonLayer data via the layerData prop.

    Only the hexagon data dict is serialized — the ScatterplotLayer
    defined in the layout is completely untouched.
    """
    triggered = ctx.triggered_id

    if triggered == "btn-load":
        points = generate_random_points(NUM_POINTS, CENTER_LAT, CENTER_LON)
        return {"hexagons": points}, f"Loaded {NUM_POINTS:,} points."
    elif triggered == "btn-clear":
        return {"hexagons": []}, "No data loaded."
    return no_update, no_update


if __name__ == "__main__":
    print(f"Starting server... Map centered at ({CENTER_LAT}, {CENTER_LON})")
    print(f"Click 'Load Data' to add {NUM_POINTS:,} random points to the HexagonLayer.")
    app.run(debug = True, port = 8053)
