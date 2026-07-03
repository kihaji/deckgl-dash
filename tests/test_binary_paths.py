"""Browser test: per-segment path colors via binary transport on the stock PathLayer
(issues #80/#39). Requires a browser; opt in with DECKGL_BROWSER_TESTS=1 --headless."""
import os
import time

import numpy as np
import pytest
from dash import Dash, html

from deckgl_dash import DeckGL
from deckgl_dash.binary import binary_data

pytestmark = pytest.mark.skipif(not os.environ.get("DECKGL_BROWSER_TESTS"),
                                reason = "browser test; set DECKGL_BROWSER_TESTS=1 (needs chromedriver + selenium>=4)")


def _severe(dash_duo):
    return [e for e in (dash_duo.get_logs() or [])
            if e.get("level") == "SEVERE" and "favicon" not in str(e.get("message", ""))]


def test_binary_pathlayer_per_vertex_colors(dash_duo):
    # Two paths (4 + 3 points), flattened, with one RGBA color per vertex
    verts = np.array([[-122.45, 37.77], [-122.43, 37.78], [-122.41, 37.77], [-122.40, 37.78],
                      [-122.44, 37.75], [-122.42, 37.74], [-122.40, 37.75]], dtype = np.float32)
    colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255], [255, 255, 0, 255],
                       [255, 0, 255, 255], [0, 255, 255, 255], [255, 128, 0, 255]], dtype = np.uint8)
    starts = np.array([0, 4], dtype = np.uint32)

    app = Dash(__name__)
    app.layout = html.Div([DeckGL(
        id = "map",
        initial_view_state = {"longitude": -122.425, "latitude": 37.765, "zoom": 12},
        style = {"width": "500px", "height": "400px", "position": "relative"},
        layers = [{"@@type": "PathLayer", "id": "paths", "widthMinPixels": 6, "_pathType": "open",
                   "data": binary_data(2, {"getPath": verts, "getColor": colors}, start_indices = starts)}],
    )])
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#map canvas")
    time.sleep(3)
    assert _severe(dash_duo) == []


def test_binary_directed_path_arrows(dash_duo):
    """Direction arrows over binary path data (issue #85), with a GPU time filter attached."""
    verts = np.array([[-122.45, 37.77], [-122.43, 37.78], [-122.41, 37.77], [-122.38, 37.79],
                      [-122.44, 37.74], [-122.42, 37.73], [-122.40, 37.74]], dtype = np.float32)
    colors = np.tile(np.array([30, 110, 230, 255], dtype = np.uint8), (7, 1))
    fv = np.array([1, 1, 1, 1, 2, 2, 2], dtype = np.float32)
    starts = np.array([0, 4], dtype = np.uint32)
    block = binary_data(2, {"getPath": verts, "getColor": colors, "getFilterValue": fv}, start_indices = starts)

    app = Dash(__name__)
    app.layout = html.Div([DeckGL(
        id = "map",
        initial_view_state = {"longitude": -122.42, "latitude": 37.76, "zoom": 11.5},
        style = {"width": "500px", "height": "400px", "position": "relative"},
        layers = [{"@@type": "DirectedPathLayer", "id": "tracks", "widthMinPixels": 4,
                   "_pathType": "open", "arrowSpacing": 60, "arrowSize": 16,
                   "data": block, "extensions": ["DataFilterExtension"]}],
        time_filter = {"domain": [0, 3], "window": 3, "current": 3, "playing": False},
    )])
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#map canvas")
    time.sleep(3)
    assert _severe(dash_duo) == []
