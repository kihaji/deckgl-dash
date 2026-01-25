"""
Performance test demo for deckgl-dash.

This example tests rendering performance with:
- H3 hexagons (res 10) as GeoJSON features: 10k, 20k, 40k, 100k layers
- HexagonLayer (aggregation): 10k, 20k, 40k, 100k point layers
- BitmapLayer: image overlay

All layers start invisible and can be toggled via checkboxes.

Requirements:
    pip install h3  # or: poetry install -E test
"""
import base64
import json
import os
import random
from pathlib import Path
from dash import Dash, html, callback, Output, Input, State, ctx, dcc, no_update

from deckgl_dash import DeckGL, ColorScale, color_range_from_scale
from deckgl_dash.layers import TileLayer, GeoJsonLayer, HexagonLayer, BitmapLayer, process_layers

try:
    import h3
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
    """Generate GeoJSON FeatureCollection with H3 hexagons.

    Generates random points in expanding radius until we have enough unique hexagons.
    """
    hexagons = set()
    radius = 0.1  # Start with ~10km radius (in degrees)

    while len(hexagons) < count:
        # Generate random points and get their H3 index
        for _ in range(count * 2):
            lat = center_lat + random.uniform(-radius, radius)
            lon = center_lon + random.uniform(-radius, radius)
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            hexagons.add(h3_index)
            if len(hexagons) >= count:
                break
        radius *= 1.5  # Expand search area if needed

    # Convert to list and trim to exact count
    hexagon_list = list(hexagons)[:count]

    # Convert to GeoJSON features with random count values
    features = []
    for h3_index in hexagon_list:
        boundary = h3.cell_to_boundary(h3_index)
        # h3 returns (lat, lng) tuples, GeoJSON needs [lng, lat]
        coordinates = [[lng, lat] for lat, lng in boundary]
        coordinates.append(coordinates[0])  # Close the polygon

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
# In debug mode, Flask runs the module twice (main + reloader), so we only print in one
H3_DATA = {}
POINT_DATA = {}
_is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
_verbose = not _is_reloader  # Only print in main process

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

# Color range for HexagonLayer using viridis scale (same as GeoJsonLayer for consistency)
COLOR_RANGE = color_range_from_scale('viridis', 6)

app = Dash(__name__)

# Create layer definitions - only include data for VISIBLE layers to reduce payload
def create_layers(visible_layers: set, extruded_3d: bool = True) -> list:
    """Create layers - only visible layers include their data to minimize transfer size."""
    layers = [
        # Base map (always visible)
        TileLayer(
            id = "osm-tiles",
            data = "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            min_zoom = 0, max_zoom = 19, tile_size = 256,
        ),
    ]

    # H3 GeoJSON layers - only add if visible
    # Using @@scale for data-driven color mapping (viridis scale, auto-domain from data)
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

    # HexagonLayer (aggregation) layers - only add if visible
    for size in LAYER_SIZES:
        layer_id = f"agg-{size // 1000}k"
        if layer_id in visible_layers:
            layers.append(
                HexagonLayer(
                    id = layer_id,
                    data = POINT_DATA[size],
                    get_position = "@@=coordinates",
                    radius = 100,  # ~100m radius to approximate H3 res 10 size
                    elevation_scale = 50 if extruded_3d else 0,
                    extruded = extruded_3d,
                    color_range = COLOR_RANGE,
                    color_aggregation = "SUM",  # Use sum of points for color
                    get_color_weight = 1,  # Each point contributes 1 to the count
                    lower_percentile = 0,  # Include all bins in color scale
                    upper_percentile = 100,
                    pickable = True,
                    auto_highlight = True,
                    highlight_color = [255, 255, 0, 180],  # Yellow highlight
                )
            )

    # Bitmap layer for image overlay - only add if visible
    if "image-overlay" in visible_layers:
        layers.append(
            BitmapLayer(
                id = "image-overlay",
                image = IMAGE_DATA_URL,
                bounds = IMAGE_BOUNDS,
                opacity = 0.8,
            )
        )

    return layers


# Initial visible layers (none)
INITIAL_VISIBLE = set()

app.layout = html.Div([
    html.H1("deckgl-dash Performance Test"),
    html.P("Toggle layers to test rendering performance. Monitor browser console and FPS."),

    # Layer toggle controls
    html.Div([
        html.Div([
            html.H4("H3 Hexagons (GeoJSON)"),
            *[dcc.Checklist(id = f"toggle-h3-{size // 1000}k", options = [{"label": f" {size // 1000}k hexagons", "value": f"h3-{size // 1000}k"}], value = [], inline = True) for size in LAYER_SIZES],
        ], style = {"display": "inline-block", "verticalAlign": "top", "marginRight": "40px"}),

        html.Div([
            html.H4("HexagonLayer (Aggregation)"),
            *[dcc.Checklist(id = f"toggle-agg-{size // 1000}k", options = [{"label": f" {size // 1000}k points", "value": f"agg-{size // 1000}k"}], value = [], inline = True) for size in LAYER_SIZES],
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

    # Store for visible layers
    dcc.Store(id = "visible-layers", data = list(INITIAL_VISIBLE)),

    # Map
    DeckGL(
        id = "map",
        layers = process_layers(create_layers(INITIAL_VISIBLE)),
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
            html.Li("H3 hexagons are rendered as GeoJSON polygon features - tests feature rendering capability"),
            html.Li("HexagonLayer uses GPU aggregation - typically more efficient for large point datasets"),
            html.Li("Watch browser DevTools Performance tab and GPU usage"),
            html.Li("Enable layers incrementally to see performance impact"),
        ])
    ], style = {"marginTop": "20px"}),
])


# Collect all toggle inputs
TOGGLE_IDS = [f"toggle-h3-{size // 1000}k" for size in LAYER_SIZES] + [f"toggle-agg-{size // 1000}k" for size in LAYER_SIZES] + ["toggle-image"]


@callback(
    Output("visible-layers", "data"),
    [Input(tid, "value") for tid in TOGGLE_IDS],
    prevent_initial_call = True,  # Don't fire on initial page load
)
def update_visible_layers(*toggle_values):
    """Combine all checkbox values into a single list of visible layer IDs."""
    visible = []
    for values in toggle_values:
        visible.extend(values or [])
    return visible


# Store for current 3D mode to detect changes
_last_3d_mode = {"value": "2d"}


@callback(
    Output("map", "layers"),
    Input("visible-layers", "data"),
    Input("toggle-3d", "value"),
    prevent_initial_call = True,
)
def update_layers(visible_layers, mode_3d):
    """Update map layers when visibility or 3D mode changes."""
    visible_set = set(visible_layers or [])
    extruded = mode_3d == "3d"
    print(f"Updating layers: {visible_set}, 3D={extruded}")
    layers = process_layers(create_layers(visible_set, extruded_3d = extruded))
    print(f"  Sending {len(layers)} layers")
    return layers


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
