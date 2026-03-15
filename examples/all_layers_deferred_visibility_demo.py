"""
All-layers deferred load + visibility toggle demo for deckgl-dash.

Tests every implemented layer type with:
- Deferred data loading via `layerData` (accumulated on the client)
- Visibility toggling via `visible` property (no data re-sent)

Usage:
    python examples/all_layers_deferred_visibility_demo.py
"""
from __future__ import annotations
import json
import math
import random
from urllib.parse import quote
from dash import Dash, html, callback, Output, Input, State, ctx, no_update
from deckgl_dash import DeckGL
from deckgl_dash.layers import (
    GeoJsonLayer, ScatterplotLayer, PathLayer, LineLayer, ArcLayer,
    IconLayer, TextLayer, PolygonLayer,
    HeatmapLayer, HexagonLayer, GridLayer,
    process_layers,
)
from deckgl_dash.layers.geo import TileLayer, MVTLayer, BitmapLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

CENTER_LON, CENTER_LAT = -83.62, 32.84

# --- Icon atlas as inline SVG data URI (single circle marker) ---
_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><circle cx="32" cy="32" r="28" fill="#E91E63"/></svg>'
ICON_ATLAS_URI = f"data:image/svg+xml;charset=utf-8,{quote(_ICON_SVG)}"
ICON_MAPPING = {"marker": {"x": 0, "y": 0, "width": 64, "height": 64, "anchorY": 64}}

# --- Bitmap image as inline SVG data URI ---
_BITMAP_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="#9C27B0" opacity="0.4"/><text x="100" y="105" text-anchor="middle" fill="white" font-size="20">Bitmap</text></svg>'
BITMAP_IMAGE_URI = f"data:image/svg+xml;charset=utf-8,{quote(_BITMAP_SVG)}"
BITMAP_BOUNDS = [CENTER_LON - 0.04, CENTER_LAT - 0.03, CENTER_LON + 0.04, CENTER_LAT + 0.03]

# Tile URL for TileLayer
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

# --- Layer registry: id, label, button color ---
LAYER_REGISTRY: list[dict] = [
    # Core layers
    {"id": "geojson", "label": "GeoJsonLayer", "color": "#2196F3"},
    {"id": "scatterplot", "label": "ScatterplotLayer", "color": "#4CAF50"},
    {"id": "path", "label": "PathLayer", "color": "#FF9800"},
    {"id": "line", "label": "LineLayer", "color": "#9C27B0"},
    {"id": "arc", "label": "ArcLayer", "color": "#00BCD4"},
    {"id": "icon", "label": "IconLayer", "color": "#E91E63"},
    {"id": "text", "label": "TextLayer", "color": "#607D8B"},
    {"id": "polygon", "label": "PolygonLayer", "color": "#795548"},
    # Geo layers
    {"id": "tile", "label": "TileLayer", "color": "#3F51B5"},
    {"id": "bitmap", "label": "BitmapLayer", "color": "#9C27B0", "preloaded": True},
    # Aggregation layers
    {"id": "heatmap", "label": "HeatmapLayer", "color": "#F44336"},
    {"id": "hexagon", "label": "HexagonLayer", "color": "#FF5722"},
    {"id": "grid", "label": "GridLayer", "color": "#8BC34A"},
]

LAYER_IDS = [lr["id"] for lr in LAYER_REGISTRY]


# ═══════════════════════════════════════════════════════════════════
# Data generators
# ═══════════════════════════════════════════════════════════════════

def _rng_lon(spread: float = 0.12) -> float:
    return CENTER_LON + random.uniform(-spread, spread)


def _rng_lat(spread: float = 0.08) -> float:
    return CENTER_LAT + random.uniform(-spread, spread)


def gen_geojson(n: int = 120) -> dict:
    features = []
    for _ in range(n):
        cx, cy = _rng_lon(), _rng_lat()
        r = random.uniform(0.0005, 0.002)
        sides = random.choice([5, 6, 7, 8])
        a0 = random.uniform(0, 2 * math.pi)
        coords = [[cx + r * math.cos(a0 + 2 * math.pi * i / sides), cy + r * math.sin(a0 + 2 * math.pi * i / sides)] for i in range(sides)]
        coords.append(coords[0])
        features.append({"type": "Feature", "properties": {"val": random.randint(1, 100)}, "geometry": {"type": "Polygon", "coordinates": [coords]}})
    return {"type": "FeatureCollection", "features": features}


def gen_scatterplot(n: int = 300) -> list[dict]:
    return [{"position": [_rng_lon(), _rng_lat()], "radius": random.randint(20, 200), "val": random.randint(1, 100)} for _ in range(n)]


def gen_paths(n: int = 60) -> list[dict]:
    paths = []
    for _ in range(n):
        x, y = _rng_lon(), _rng_lat()
        coords = [[x, y]]
        for _ in range(random.randint(3, 8)):
            x += random.uniform(-0.008, 0.008)
            y += random.uniform(-0.005, 0.005)
            coords.append([x, y])
        paths.append({"path": coords})
    return paths


def gen_lines(n: int = 80) -> list[dict]:
    return [{"source": [_rng_lon(), _rng_lat()], "target": [_rng_lon(), _rng_lat()]} for _ in range(n)]


def gen_arcs(n: int = 60) -> list[dict]:
    return [{"source": [_rng_lon(), _rng_lat()], "target": [_rng_lon(), _rng_lat()]} for _ in range(n)]


def gen_icons(n: int = 80) -> list[dict]:
    return [{"position": [_rng_lon(), _rng_lat()], "icon": "marker", "size": random.randint(15, 40)} for _ in range(n)]


PLACE_NAMES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa",
               "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon"]


def gen_text(n: int = 40) -> list[dict]:
    return [{"position": [_rng_lon(), _rng_lat()], "label": random.choice(PLACE_NAMES)} for _ in range(n)]


def gen_polygons(n: int = 80) -> list[dict]:
    polys = []
    for _ in range(n):
        cx, cy = _rng_lon(), _rng_lat()
        r = random.uniform(0.001, 0.003)
        sides = random.choice([4, 5, 6])
        a0 = random.uniform(0, 2 * math.pi)
        coords = [[cx + r * math.cos(a0 + 2 * math.pi * i / sides), cy + r * math.sin(a0 + 2 * math.pi * i / sides)] for i in range(sides)]
        coords.append(coords[0])
        polys.append({"polygon": coords, "val": random.randint(1, 100)})
    return polys


def gen_points(n: int = 500) -> list[dict]:
    """Generic point data for aggregation layers (heatmap, hexagon, grid)."""
    return [{"coordinates": [_rng_lon(), _rng_lat()], "weight": random.randint(1, 50)} for _ in range(n)]


DATA_GENERATORS: dict[str, callable] = {  # type: ignore[type-arg]
    "geojson": gen_geojson,
    "scatterplot": gen_scatterplot,
    "path": gen_paths,
    "line": gen_lines,
    "arc": gen_arcs,
    "icon": gen_icons,
    "text": gen_text,
    "polygon": gen_polygons,
    "tile": lambda: OSM_TILE_URL,
    "heatmap": gen_points,
    "hexagon": gen_points,
    "grid": gen_points,
}


# ═══════════════════════════════════════════════════════════════════
# Layer builder
# ═══════════════════════════════════════════════════════════════════

def _build_layers(visibility: dict[str, bool]) -> list[dict] | None:
    """Build all layer configs with current visibility. Data is always empty (layerData provides it)."""
    return process_layers([
        GeoJsonLayer(
            id = "geojson", data = [], get_fill_color = [33, 150, 243, 160], get_line_color = [25, 118, 210],
            line_width_min_pixels = 1, filled = True, stroked = True, pickable = True, visible = visibility.get("geojson", True),
        ),
        ScatterplotLayer(
            id = "scatterplot", data = [], get_position = "@@=position", get_radius = "@@=radius",
            get_fill_color = [76, 175, 80, 180], radius_min_pixels = 2, pickable = True, visible = visibility.get("scatterplot", True),
        ),
        PathLayer(
            id = "path", data = [], get_path = "@@=path", get_color = [255, 152, 0], get_width = 3,
            width_min_pixels = 2, pickable = True, visible = visibility.get("path", True),
        ),
        LineLayer(
            id = "line", data = [], get_source_position = "@@=source", get_target_position = "@@=target",
            get_color = [156, 39, 176], get_width = 2, width_min_pixels = 1, pickable = True, visible = visibility.get("line", True),
        ),
        ArcLayer(
            id = "arc", data = [], get_source_position = "@@=source", get_target_position = "@@=target",
            get_source_color = [0, 188, 212], get_target_color = [0, 150, 136], get_width = 2,
            width_min_pixels = 1, pickable = True, visible = visibility.get("arc", True),
        ),
        IconLayer(
            id = "icon", data = [], get_position = "@@=position", get_icon = "@@=icon", get_size = "@@=size",
            icon_atlas = ICON_ATLAS_URI, icon_mapping = ICON_MAPPING,
            size_min_pixels = 10, pickable = True, visible = visibility.get("icon", True),
        ),
        TextLayer(
            id = "text", data = [], get_position = "@@=position", get_text = "@@=label",
            get_size = 14, get_color = [96, 125, 139], background = True, background_color = [255, 255, 255, 200],
            pickable = True, visible = visibility.get("text", True),
        ),
        PolygonLayer(
            id = "polygon", data = [], get_polygon = "@@=polygon", get_fill_color = [121, 85, 72, 140],
            get_line_color = [93, 64, 55], get_line_width = 2, line_width_min_pixels = 1,
            filled = True, stroked = True, pickable = True, visible = visibility.get("polygon", True),
        ),
        TileLayer(
            id = "tile", data = "", min_zoom = 0, max_zoom = 19,
            opacity = 0.3, visible = visibility.get("tile", True),
        ),
        BitmapLayer(
            id = "bitmap", image = BITMAP_IMAGE_URI, bounds = BITMAP_BOUNDS,
            opacity = 0.6, visible = visibility.get("bitmap", True),
        ),
        HeatmapLayer(
            id = "heatmap", data = [], get_position = "@@=coordinates", get_weight = "@@=weight",
            radius_pixels = 30, intensity = 1, threshold = 0.05, visible = visibility.get("heatmap", True),
        ),
        HexagonLayer(
            id = "hexagon", data = [], get_position = "@@=coordinates", radius = 200,
            extruded = False, opacity = 0.5, pickable = True, visible = visibility.get("hexagon", True),
        ),
        GridLayer(
            id = "grid", data = [], get_position = "@@=coordinates", cell_size = 200,
            extruded = False, opacity = 0.5, pickable = True, visible = visibility.get("grid", True),
        ),
    ])


# ═══════════════════════════════════════════════════════════════════
# App layout
# ═══════════════════════════════════════════════════════════════════

def _btn(label: str, id_dict: dict, color: str) -> html.Button:
    return html.Button(label, id = id_dict, n_clicks = 0, style = {
        "padding": "4px 12px", "fontSize": "12px", "cursor": "pointer", "border": "none",
        "borderRadius": "3px", "color": "white", "backgroundColor": color, "marginRight": "4px",
    })


def _layer_row(reg: dict) -> html.Div:
    lid = reg["id"]
    color = reg["color"]
    children: list = [
        html.Span(reg["label"], style = {"fontWeight": "bold", "width": "140px", "display": "inline-block", "fontSize": "12px"}),
    ]
    if not reg.get("preloaded"):
        children.append(_btn("Load", {"type": "btn-load", "layer": lid}, color))
    else:
        children.append(html.Span("(preloaded)", style = {"fontSize": "11px", "color": "#999", "marginRight": "4px", "width": "60px", "display": "inline-block"}))
    children.extend([
        _btn("Toggle", {"type": "btn-toggle", "layer": lid}, "#757575"),
        html.Span(id = {"type": "status", "layer": lid},
                  children = "preloaded" if reg.get("preloaded") else "empty",
                  style = {"fontSize": "11px", "color": "#888", "marginLeft": "4px"}),
    ])
    return html.Div(children, style = {"display": "flex", "alignItems": "center", "marginBottom": "4px"})


app = Dash(__name__)

default_vis = {lid: True for lid in LAYER_IDS}

app.layout = html.Div([
    html.H2("All Layers — Deferred Load + Visibility Toggle", style = {"marginBottom": "8px"}),
    html.P("Each layer starts empty. Click Load to send data, Toggle to show/hide. "
           "Layers accumulate independently — loading one never re-sends another.",
           style = {"fontSize": "13px", "color": "#666", "marginBottom": "10px"}),

    # Controls
    html.Div(
        [_layer_row(reg) for reg in LAYER_REGISTRY],
        style = {"marginBottom": "10px", "padding": "10px", "backgroundColor": "#f5f5f5",
                 "borderRadius": "5px", "maxHeight": "320px", "overflowY": "auto"},
    ),

    # Visibility store
    html.Div(id = "visibility-store", children = json.dumps(default_vis), style = {"display": "none"}),

    DeckGL(
        id = "map",
        maplibre_config = MapLibreConfig(
            style = MapLibreStyle.CARTO_POSITRON,
            map_options = {"dragRotate": False, "touchRotate": False, "keyboard": False, "maxPitch": 0},
        ).to_dict(),
        layers = _build_layers(default_vis),
        initial_view_state = {"longitude": CENTER_LON, "latitude": CENTER_LAT, "zoom": 13, "pitch": 0, "bearing": 0},
        enable_events = ["click"],
        style = {"width": "100%", "height": "600px"},
    ),
], style = {"padding": "15px", "fontFamily": "sans-serif"})


# ═══════════════════════════════════════════════════════════════════
# Callbacks
# ═══════════════════════════════════════════════════════════════════

# Build Output list for all status spans
_status_outputs = [Output({"type": "status", "layer": lid}, "children") for lid in LAYER_IDS]
_load_inputs = [Input({"type": "btn-load", "layer": lid}, "n_clicks") for lid in LAYER_IDS if lid not in ("bitmap",)]


@callback(
    Output("map", "layerData"),
    *_status_outputs,
    *_load_inputs,
    prevent_initial_call = True,
)
def load_data(*args):  # type: ignore[no-untyped-def]
    """Load data for the triggered layer via layerData."""
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return (no_update,) * (1 + len(LAYER_IDS))

    layer_id = triggered.get("layer")
    generator = DATA_GENERATORS.get(layer_id)  # type: ignore[arg-type]
    if not generator:
        return (no_update,) * (1 + len(LAYER_IDS))

    data = generator()
    count = len(data) if isinstance(data, (list, dict)) else "URL"
    if isinstance(data, dict) and "features" in data:
        count = len(data["features"])

    # Build status updates: only update the triggered layer's status
    statuses: list = [no_update] * len(LAYER_IDS)
    idx = LAYER_IDS.index(layer_id)
    statuses[idx] = f"loaded ({count})"

    return ({layer_id: data}, *statuses)


@callback(
    Output("map", "layers"),
    Output("visibility-store", "children"),
    [Input({"type": "btn-toggle", "layer": lid}, "n_clicks") for lid in LAYER_IDS],
    State("visibility-store", "children"),
    prevent_initial_call = True,
)
def toggle_visibility(*args):  # type: ignore[no-untyped-def]
    """Toggle layer visibility by updating layers prop (no data re-sent)."""
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return no_update, no_update

    vis_json = args[-1]  # last arg is State
    vis = json.loads(vis_json)
    layer_id = triggered["layer"]
    vis[layer_id] = not vis.get(layer_id, True)

    return _build_layers(vis), json.dumps(vis)


if __name__ == "__main__":
    print(f"Starting server... {len(LAYER_REGISTRY)} layer types")
    print(f"Map centered at ({CENTER_LAT}, {CENTER_LON})")
    app.run(debug = True, port = 8055)
