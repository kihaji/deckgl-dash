"""Regression test for issue #9 / T-02: toggling maplibreConfig via callback must not crash React.

The MapLibre early return in DeckGL.react.js used to sit above a useMemo, so switching modes
changed the hook count between renders ("Rendered fewer hooks than expected").
Requires a browser (chromedriver on PATH + selenium>=4); opt in with:
    DECKGL_BROWSER_TESTS=1 poetry run pytest tests/test_maplibre_toggle.py --headless
"""
import os
import time
import pytest
from dash import Dash, html, Input, Output
from deckgl_dash import DeckGL

pytestmark = pytest.mark.skipif(not os.environ.get("DECKGL_BROWSER_TESTS"),
                                reason = "browser test; set DECKGL_BROWSER_TESTS=1 (needs chromedriver + selenium>=4)")

MAPLIBRE_CONFIG = {"mapStyle": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"}
VIEW_STATE = {"longitude": 0, "latitude": 0, "zoom": 2}


def test_toggle_maplibre_config_does_not_crash(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("toggle", id = "toggle"),
        html.Div(id = "status"),
        DeckGL(id = "deck", initial_view_state = VIEW_STATE, layers = [], style = {"width": "400px", "height": "300px", "position": "relative"}),
    ])

    @app.callback(Output("deck", "maplibreConfig"), Output("status", "children"), Input("toggle", "n_clicks"))
    def toggle(n_clicks):
        n = n_clicks or 0
        return (MAPLIBRE_CONFIG if n % 2 == 1 else None), f"toggled-{n}"

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#deck")

    # deck-only -> maplibre -> deck-only: the second switch is where the stale hook count crashed
    for i in range(1, 4):
        dash_duo.find_element("#toggle").click()
        dash_duo.wait_for_text_to_equal("#status", f"toggled-{i}", timeout = 10)
        time.sleep(0.5)

    hook_errors = [entry for entry in (dash_duo.get_logs() or []) if "hooks" in str(entry.get("message", "")).lower()]
    assert hook_errors == [], f"React hooks error after toggling maplibreConfig: {hook_errors}"
    # The component should still be mounted (Dash error boundary would replace it on crash)
    assert dash_duo.find_element("#deck") is not None
