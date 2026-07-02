"""
Demo: per-segment path colors via binary transport (stock PathLayer).

The JSON-mode equivalent needs PathLayer(multi_color=True); in binary mode the stock
PathLayer consumes a per-vertex color attribute directly — write segment i's color at
vertex i (the last vertex's color is unused). Scales to hundreds of thousands of
segments with a fraction of the JSON payload and parse cost.

Requires numpy: pip install deckgl-dash[binary]
"""
import numpy as np
from dash import Dash, html

from deckgl_dash import DeckGL
from deckgl_dash.binary import binary_data

# 60 tracks x 120 segments of random-walk paths around San Francisco
N_PATHS, N_PTS = 60, 121
rng = np.random.default_rng(7)
starts = (np.arange(N_PATHS, dtype = np.uint32) * N_PTS)
origins = rng.uniform([-122.52, 37.70], [-122.36, 37.83], size = (N_PATHS, 1, 2))
steps = rng.normal(0, 0.0012, size = (N_PATHS, N_PTS, 2)).cumsum(axis = 1)
verts = (origins + steps).astype(np.float32).reshape(-1, 2)

# Color each SEGMENT by its speed (step length): blue = slow, red = fast.
seg = verts.reshape(N_PATHS, N_PTS, 2)
speed = np.linalg.norm(np.diff(seg, axis = 1), axis = 2)                       # (paths, pts-1)
t = np.clip(speed / np.percentile(speed, 95), 0, 1)
colors = np.zeros((N_PATHS, N_PTS, 4), dtype = np.uint8)
colors[..., :N_PTS - 1 + 1, 3] = 255
colors[:, :-1, 0] = (t * 255).astype(np.uint8)        # red rises with speed
colors[:, :-1, 2] = ((1 - t) * 255).astype(np.uint8)  # blue falls
colors[:, -1] = colors[:, -2]                          # final vertex color is unused; mirror it
colors = colors.reshape(-1, 4)

app = Dash(__name__)
app.layout = html.Div([
    html.H3("Binary per-segment path colors — 60 tracks colored by segment speed"),
    DeckGL(
        id = "map",
        initial_view_state = {"longitude": -122.44, "latitude": 37.765, "zoom": 11.5},
        style = {"width": "100%", "height": "620px", "position": "relative"},
        layers = [
            {"@@type": "TileLayer", "id": "basemap", "data": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
             "minZoom": 0, "maxZoom": 19, "tileSize": 256},
            {"@@type": "PathLayer", "id": "tracks", "widthMinPixels": 3, "_pathType": "open",
             "data": binary_data(N_PATHS, {"getPath": verts, "getColor": colors}, start_indices = starts)},
        ],
    ),
])

if __name__ == "__main__":
    app.run(debug = True, port = 8058)
