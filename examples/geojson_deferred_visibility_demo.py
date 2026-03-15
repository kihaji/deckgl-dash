"""
Deferred GeoJsonLayer data loading + visibility toggle demo for deckgl-dash.

Demonstrates:
- Initializing two GeoJsonLayers with empty data
- Loading data into each via the `layerData` prop (deferred)
- Toggling layer visibility without re-sending data

Usage:
    python examples/geojson_deferred_visibility_demo.py
"""
import random
import json
from dash import Dash, html, callback, Output, Input, State, ctx, no_update, ALL
from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer, process_layers
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

CENTER_LON, CENTER_LAT = -83.62, 32.84
NUM_POLYGONS = 200
NUM_LINES = 150

LAYER_DEFS = [
    {"id": "polygons", "label": "Polygons", "color": "#2196F3"},
    {"id": "lines", "label": "Lines", "color": "#FF5722"},
]


def _random_polygon(center_lon: float, center_lat: float, radius: float = 0.002, sides: int = 6) -> dict:
    """Generate a single random GeoJSON polygon feature."""
    import math
    cx = center_lon + random.uniform(-0.12, 0.12)
    cy = center_lat + random.uniform(-0.08, 0.08)
    r = random.uniform(radius * 0.3, radius)
    angle_offset = random.uniform(0, 2 * math.pi)
    coords = []
    for i in range(sides):
        a = angle_offset + 2 * math.pi * i / sides
        coords.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    coords.append(coords[0])
    return {
        "type": "Feature",
        "properties": {"value": random.randint(1, 100)},
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


def _random_line(center_lon: float, center_lat: float, segments: int = 4) -> dict:
    """Generate a single random GeoJSON linestring feature."""
    x = center_lon + random.uniform(-0.12, 0.12)
    y = center_lat + random.uniform(-0.08, 0.08)
    coords = [[x, y]]
    for _ in range(segments):
        x += random.uniform(-0.01, 0.01)
        y += random.uniform(-0.01, 0.01)
        coords.append([x, y])
    return {
        "type": "Feature",
        "properties": {"speed": random.randint(10, 80)},
        "geometry": {"type": "LineString", "coordinates": coords},
    }


def generate_polygons(n: int) -> dict:
    return {"type": "FeatureCollection", "features": [_random_polygon(CENTER_LON, CENTER_LAT) for _ in range(n)]}


def generate_lines(n: int) -> dict:
    return {"type": "FeatureCollection", "features": [_random_line(CENTER_LON, CENTER_LAT) for _ in range(n)]}


def _make_layers(visibility: dict[str, bool]) -> list[dict] | None:
    """Build the layer config list with current visibility (data always empty — layerData provides it)."""
    return process_layers([
        GeoJsonLayer(
            id = "polygons",
            data = [],
            get_fill_color = [33, 150, 243, 160],
            get_line_color = [25, 118, 210],
            line_width_min_pixels = 1,
            filled = True,
            stroked = True,
            pickable = True,
            auto_highlight = True,
            visible = visibility.get("polygons", True),
        ),
        GeoJsonLayer(
            id = "lines",
            data = [],
            get_line_color = [255, 87, 34],
            get_line_width = 3,
            line_width_min_pixels = 2,
            pickable = True,
            auto_highlight = True,
            visible = visibility.get("lines", True),
        ),
    ])


def _btn_style(color: str, active: bool = True) -> dict:
    return {
        "padding": "8px 18px", "fontSize": "14px", "cursor": "pointer", "border": "none",
        "borderRadius": "4px", "color": "white", "marginRight": "8px",
        "backgroundColor": color if active else "#9E9E9E",
        "opacity": "1" if active else "0.7",
    }


app = Dash(__name__)

app.layout = html.Div([
    html.H1("GeoJsonLayer Deferred Load + Visibility Demo"),
    html.P("Both layers start empty. Load data independently, then toggle visibility without re-sending data."),

    # Controls
    html.Div([
        html.Div([
            html.Button("Load Polygons", id = {"type": "btn-load", "layer": "polygons"}, n_clicks = 0,
                        style = _btn_style("#2196F3")),
            html.Button("Toggle Polygons", id = {"type": "btn-toggle", "layer": "polygons"}, n_clicks = 0,
                        style = _btn_style("#1976D2")),
            html.Span(id = {"type": "status", "layer": "polygons"}, children = "No data",
                      style = {"fontSize": "13px", "color": "#666"}),
        ], style = {"marginBottom": "8px", "display": "flex", "alignItems": "center"}),
        html.Div([
            html.Button("Load Lines", id = {"type": "btn-load", "layer": "lines"}, n_clicks = 0,
                        style = _btn_style("#FF5722")),
            html.Button("Toggle Lines", id = {"type": "btn-toggle", "layer": "lines"}, n_clicks = 0,
                        style = _btn_style("#E64A19")),
            html.Span(id = {"type": "status", "layer": "lines"}, children = "No data",
                      style = {"fontSize": "13px", "color": "#666"}),
        ], style = {"display": "flex", "alignItems": "center"}),
    ], style = {"marginBottom": "15px", "padding": "12px", "backgroundColor": "#f5f5f5", "borderRadius": "5px"}),

    # Hidden store for visibility state
    html.Div(id = "visibility-store", children = json.dumps({"polygons": True, "lines": True}),
             style = {"display": "none"}),

    DeckGL(
        id = "map",
        maplibre_config = MapLibreConfig(
            style = MapLibreStyle.CARTO_POSITRON,
            map_options = {"dragRotate": False, "touchRotate": False, "keyboard": False, "maxPitch": 0},
        ).to_dict(),
        layers = _make_layers({"polygons": True, "lines": True}),
        initial_view_state = {"longitude": CENTER_LON, "latitude": CENTER_LAT, "zoom": 12, "pitch": 0, "bearing": 0},
        enable_events = ["click"],
        tooltip = {
            "layers": {
                "polygons": {"html": "<b>Polygon value:</b> {properties.value}"},
                "lines": {"html": "<b>Line speed:</b> {properties.speed}"},
            },
        },
        style = {"width": "100%", "height": "700px"},
    ),
], style = {"padding": "20px", "fontFamily": "sans-serif"})


@callback(
    Output("map", "layerData"),
    Output({"type": "status", "layer": "polygons"}, "children"),
    Output({"type": "status", "layer": "lines"}, "children"),
    Input({"type": "btn-load", "layer": "polygons"}, "n_clicks"),
    Input({"type": "btn-load", "layer": "lines"}, "n_clicks"),
    prevent_initial_call = True,
)
def load_data(poly_clicks, line_clicks):
    """Load GeoJSON data into the targeted layer via layerData."""
    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update, no_update

    layer_id = triggered["layer"]
    if layer_id == "polygons":
        data = generate_polygons(NUM_POLYGONS)
        return {"polygons": data}, f"Loaded {NUM_POLYGONS} polygons", no_update
    elif layer_id == "lines":
        data = generate_lines(NUM_LINES)
        return {"lines": data}, no_update, f"Loaded {NUM_LINES} lines"
    return no_update, no_update, no_update


@callback(
    Output("map", "layers"),
    Output("visibility-store", "children"),
    Input({"type": "btn-toggle", "layer": "polygons"}, "n_clicks"),
    Input({"type": "btn-toggle", "layer": "lines"}, "n_clicks"),
    State("visibility-store", "children"),
    prevent_initial_call = True,
)
def toggle_visibility(poly_clicks, line_clicks, vis_json):
    """Toggle layer visibility by updating layers prop (no data re-sent)."""
    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update

    vis = json.loads(vis_json)
    layer_id = triggered["layer"]
    vis[layer_id] = not vis[layer_id]

    return _make_layers(vis), json.dumps(vis)


if __name__ == "__main__":
    print(f"Starting server... Map centered at ({CENTER_LAT}, {CENTER_LON})")
    print(f"Load {NUM_POLYGONS} polygons and {NUM_LINES} lines independently, then toggle visibility.")
    app.run(debug = True, port = 8054)
