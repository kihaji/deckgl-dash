"""
Performance test demo for deckgl-dash.

This example tests rendering performance with:
- H3 hexagons (res 10) as GeoJSON features: 10k, 20k, 40k, 100k layers
- HexagonLayer (aggregation): 10k, 20k, 40k, 100k point layers
- BitmapLayer: image overlay

HexagonLayers demonstrate the `layerData` prop with `Patch()` — each toggle
callback updates only its own layer's data, without touching other layers.

Requirements:
    pip install h3  # or: poetry install -E test
"""
import base64
import json
import os
import random
from pathlib import Path
from dash import Dash, html, callback, Output, Input, State, ctx, dcc, no_update, ALL, MATCH, Patch

from deckgl_dash import DeckGL, ColorScale, color_range_from_scale
from deckgl_dash.layers import TileLayer, GeoJsonLayer, HexagonLayer, BitmapLayer, process_layers

try:
    import h3  # type: ignore[reportMissingImports]
except ImportError:
    raise ImportError("h3 is required for this demo. Install with: pip install h3")

# Load image bounds and encode image as base64 data URL
# Using NASA VIIRS satellite imagery (public domain) of San Francisco Bay Area
BOUNDS_FILE = Path(__file__).parent / "sf_satellite_bounds.json"
IMAGE_FILE = Path(__file__).parent / "sf_satellite.png"

with open(BOUNDS_FILE) as f:
    bounds_data = json.load(f)

with open(IMAGE_FILE, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
IMAGE_DATA_URL = f"data:image/png;base64,{image_b64}"

IMAGE_BOUNDS = [bounds_data["lon_min"], bounds_data["lat_min"], bounds_data["lon_max"], bounds_data["lat_max"]]
CENTER_LAT = (bounds_data["lat_min"] + bounds_data["lat_max"]) / 2
CENTER_LON = (bounds_data["lon_min"] + bounds_data["lon_max"]) / 2

# H3 resolution 10: ~66m edge length, ~0.015 km² area
H3_RESOLUTION = 10
LAYER_SIZES = [10_000, 20_000, 40_000, 100_000]


def generate_h3_hexagons(count: int, center_lat: float, center_lon: float, resolution: int = 10) -> dict:
    """Generate GeoJSON FeatureCollection with H3 hexagons."""
    hexagons = set()
    radius = 0.1

    while len(hexagons) < count:
        for _ in range(count * 2):
            lat = center_lat + random.uniform(-radius, radius)
            lon = center_lon + random.uniform(-radius, radius)
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            hexagons.add(h3_index)
            if len(hexagons) >= count:
                break
        radius *= 1.5

    hexagon_list = list(hexagons)[:count]
    features = []
    for h3_index in hexagon_list:
        boundary = h3.cell_to_boundary(h3_index)
        coordinates = [[lng, lat] for lat, lng in boundary]
        coordinates.append(coordinates[0])
        features.append({
            "type": "Feature",
            "properties": {"h3_index": h3_index, "count": random.randint(1, 100)},
            "geometry": {"type": "Polygon", "coordinates": [coordinates]}
        })

    return {"type": "FeatureCollection", "features": features}


def generate_random_points(count: int, center_lat: float, center_lon: float, radius: float = 0.3) -> list:
    """Generate random point data for HexagonLayer aggregation."""
    return [
        {"coordinates": [center_lon + random.uniform(-radius, radius), center_lat + random.uniform(-radius, radius)], "value": random.randint(1, 100)}
        for _ in range(count)
    ]


# Pre-generate all data at startup
H3_DATA = {}
POINT_DATA = {}
_is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
_verbose = not _is_reloader

if _verbose:
    print("Generating test data (this may take a moment for larger datasets)...")

for size in LAYER_SIZES:
    if _verbose:
        print(f"  Generating {size:,} H3 hexagons...", end = " ", flush = True)
    H3_DATA[size] = generate_h3_hexagons(size, CENTER_LAT, CENTER_LON, H3_RESOLUTION)
    if _verbose:
        print(f"done ({len(H3_DATA[size]['features']):,} features)")

for size in LAYER_SIZES:
    if _verbose:
        print(f"  Generating {size:,} random points...", end = " ", flush = True)
    POINT_DATA[size] = generate_random_points(size, CENTER_LAT, CENTER_LON)
    if _verbose:
        print(f"done ({len(POINT_DATA[size]):,} points)")

if _verbose:
    print("Data generation complete.")

# Color range for HexagonLayer
COLOR_RANGE = color_range_from_scale('viridis', 6)

app = Dash(__name__)


def create_base_layers() -> list:
    """Create base layers that are always present."""
    return [
        TileLayer(
            id = "osm-tiles",
            data = "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            min_zoom = 0, max_zoom = 19, tile_size = 256,
        ),
    ]


def create_geojson_layers(visible_layers: set) -> list:
    """Create H3 GeoJSON layers - only visible ones include data."""
    layers = []
    geojson_color_scale = ColorScale('viridis').domain(1, 100).alpha(180).accessor('properties.count')

    for size in LAYER_SIZES:
        layer_id = f"h3-{size // 1000}k"
        if layer_id in visible_layers:
            layers.append(
                GeoJsonLayer(
                    id = layer_id,
                    data = H3_DATA[size],
                    filled = True, stroked = True,
                    get_fill_color = geojson_color_scale,
                    get_line_color = [0, 0, 0, 100],
                    get_line_width = 1,
                    line_width_min_pixels = 1,
                    pickable = True,
                    auto_highlight = True,
                    highlight_color = [255, 255, 0, 180],
                )
            )
    return layers


def create_bitmap_layer(visible: bool) -> list:
    """Create bitmap layer if visible."""
    if visible:
        return [BitmapLayer(
            id = "image-overlay",
            image = IMAGE_DATA_URL,
            bounds = IMAGE_BOUNDS,
            opacity = 0.8,
        )]
    return []


def build_initial_layers(extruded_3d: bool = False) -> list:
    """Build the initial layer stack with empty HexagonLayer placeholders."""
    layers = create_base_layers()
    for size in LAYER_SIZES:
        layers.append(HexagonLayer(
            id = f"agg-{size // 1000}k",
            data = [],
            get_position = "@@=coordinates",
            radius = 100,
            elevation_scale = 50 if extruded_3d else 0,
            extruded = extruded_3d,
            color_range = COLOR_RANGE,
            color_aggregation = "SUM",
            get_color_weight = 1,
            lower_percentile = 0,
            upper_percentile = 100,
            pickable = False,
            auto_highlight = False,
            highlight_color = [255, 255, 0, 180],
        ))
    return layers


# Initial state
INITIAL_VISIBLE = set()

app.layout = html.Div([
    html.H1("deckgl-dash Performance Test"),
    html.P("Toggle layers to test rendering performance. HexagonLayers use the layerData prop with Patch() for independent updates."),

    # Layer toggle controls
    html.Div([
        html.Div([
            html.H4("H3 Hexagons (GeoJSON)"),
            html.P("(rebuilds all layers)", style = {"fontSize": "0.8em", "color": "#666", "margin": "0"}),
            *[dcc.Checklist(id = f"toggle-h3-{size // 1000}k", options = [{"label": f" {size // 1000}k hexagons", "value": f"h3-{size // 1000}k"}], value = [], inline = True) for size in LAYER_SIZES],
        ], style = {"display": "inline-block", "verticalAlign": "top", "marginRight": "40px"}),

        html.Div([
            html.H4("HexagonLayer (Aggregation)"),
            html.P("(independent via layerData)", style = {"fontSize": "0.8em", "color": "#666", "margin": "0"}),
            *[dcc.Checklist(id = {"type": "toggle-agg", "size": size}, options = [{"label": f" {size // 1000}k points", "value": "visible"}], value = [], inline = True) for size in LAYER_SIZES],
        ], style = {"display": "inline-block", "verticalAlign": "top", "marginRight": "40px"}),

        html.Div([
            html.H4("Image Overlay"),
            dcc.Checklist(id = "toggle-image", options = [{"label": " Show image", "value": "image-overlay"}], value = [], inline = True),
        ], style = {"display": "inline-block", "verticalAlign": "top", "marginRight": "40px"}),

        html.Div([
            html.H4("HexagonLayer Mode"),
            dcc.RadioItems(id = "toggle-3d", options = [{"label": " 2D", "value": "2d"}, {"label": " 3D", "value": "3d"}], value = "2d", inline = True),
        ], style = {"display": "inline-block", "verticalAlign": "top"}),
    ], style = {"marginBottom": "20px", "padding": "10px", "backgroundColor": "#f5f5f5", "borderRadius": "5px"}),

    # Stores for H3/GeoJSON visibility (combined) and image visibility
    dcc.Store(id = "visible-h3-layers", data = []),
    dcc.Store(id = "visible-image", data = False),
    dcc.Store(id = "mode-3d", data = "2d"),

    # Map — HexagonLayers defined with empty data, filled via layerData
    DeckGL(
        id = "map",
        layers = process_layers(build_initial_layers()),
        initial_view_state = {"longitude": CENTER_LON, "latitude": CENTER_LAT, "zoom": 10, "pitch": 0, "bearing": 0},
        controller = {"dragRotate": False, "touchRotate": False, "keyboard": {"rotateKey": False}},
        tooltip = {
            "layers": {
                **{f"h3-{size // 1000}k": {"html": "<b>H3 Index:</b> {h3_index}<br><b>Count:</b> {count}"} for size in LAYER_SIZES},
                **{f"agg-{size // 1000}k": {"html": "<b>Point Count:</b> {colorValue}"} for size in LAYER_SIZES},
            },
            "default": {"html": "Hover for info"},
        },
        style = {"width": "100%", "height": "700px"},
    ),

    html.Div([
        html.H4("Performance Notes:"),
        html.Ul([
            html.Li("H3 GeoJSON toggles rebuild all layers (traditional pattern)"),
            html.Li("HexagonLayer toggles use layerData + Patch() — only that layer's data is sent"),
            html.Li("Watch browser DevTools Network tab to see payload sizes"),
            html.Li("Independent callbacks allow different parts of an app to manage their own layers"),
        ])
    ], style = {"marginTop": "20px"}),
])


# --- Independent callbacks for each HexagonLayer via layerData + Patch() ---

@callback(
    Output("map", "layerData"),
    Input({"type": "toggle-agg", "size": MATCH}, "value"),
    State({"type": "toggle-agg", "size": MATCH}, "id"),
    prevent_initial_call = True,
)
def update_hexagon_data(toggle_value, toggle_id):
    """Update a single HexagonLayer's data via layerData + Patch().

    Only the targeted layer's data is serialized — no other layers are affected.
    """
    size = toggle_id["size"]
    layer_id = f"agg-{size // 1000}k"
    is_visible = "visible" in (toggle_value or [])

    patched = Patch()
    if is_visible:
        print(f"[Callback] Loading data for {layer_id} ({size:,} points)")
        patched[layer_id] = POINT_DATA[size]
    else:
        print(f"[Callback] Clearing data for {layer_id}")
        patched[layer_id] = []
    return patched


# --- Callbacks for H3/GeoJSON layers (traditional pattern — rebuilds layers) ---

@callback(
    Output("visible-h3-layers", "data"),
    [Input(f"toggle-h3-{size // 1000}k", "value") for size in LAYER_SIZES],
    prevent_initial_call = True,
)
def update_h3_visibility(*toggle_values):
    """Combine H3 checkbox values into visibility list."""
    visible = []
    for values in toggle_values:
        visible.extend(values or [])
    print(f"[Callback] H3 visibility changed: {visible}")
    return visible


@callback(
    Output("visible-image", "data"),
    Input("toggle-image", "value"),
    prevent_initial_call = True,
)
def update_image_visibility(value):
    """Update image visibility."""
    visible = "image-overlay" in (value or [])
    print(f"[Callback] Image visibility: {visible}")
    return visible


@callback(
    Output("mode-3d", "data"),
    Input("toggle-3d", "value"),
    prevent_initial_call = True,
)
def update_3d_mode(value):
    """Update 3D mode."""
    print(f"[Callback] 3D mode: {value}")
    return value


# --- Layers rebuild for H3/GeoJSON/image/3D mode changes ---

@callback(
    Output("map", "layers"),
    Input("visible-h3-layers", "data"),
    Input("visible-image", "data"),
    Input("mode-3d", "data"),
    prevent_initial_call = True,
)
def rebuild_layers(h3_visible, image_visible, mode_3d):
    """Rebuild the layer stack when H3 visibility, image, or 3D mode changes.

    HexagonLayer data is NOT included here — it comes from layerData.
    Only the layer structure/styling is rebuilt.
    """
    extruded = mode_3d == "3d"

    layers = create_base_layers()
    layers.extend(create_geojson_layers(set(h3_visible or [])))

    # Add HexagonLayers with empty data — layerData fills them independently
    for size in LAYER_SIZES:
        layers.append(HexagonLayer(
            id = f"agg-{size // 1000}k",
            data = [],
            get_position = "@@=coordinates",
            radius = 100,
            elevation_scale = 50 if extruded else 0,
            extruded = extruded,
            color_range = COLOR_RANGE,
            color_aggregation = "SUM",
            get_color_weight = 1,
            lower_percentile = 0,
            upper_percentile = 100,
            pickable = False,
            auto_highlight = False,
            highlight_color = [255, 255, 0, 180],
        ))

    layers.extend(create_bitmap_layer(image_visible))

    print(f"[Callback] Rebuilding layers: {len(layers)} total, H3={h3_visible}, image={image_visible}")
    return process_layers(layers)


@callback(
    Output("map", "controller"),
    Input("toggle-3d", "value"),
    prevent_initial_call = True,
)
def update_controller(mode_3d):
    """Update controller settings when 3D mode changes."""
    if mode_3d == "3d":
        return {"dragPan": True, "scrollZoom": True, "doubleClickZoom": True, "dragRotate": True, "touchRotate": True, "touchZoom": True}
    else:
        return {"dragPan": True, "scrollZoom": True, "doubleClickZoom": True, "dragRotate": False, "touchRotate": False, "touchZoom": True}


if __name__ == "__main__":
    print(f"\nStarting server... Map centered at ({CENTER_LAT:.4f}, {CENTER_LON:.4f})")
    print(f"Image bounds: {IMAGE_BOUNDS}")
    app.run(debug = True, port = 8052)
