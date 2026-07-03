"""Dash integration smoke test (issue #29): renders the real component in a browser
and round-trips props through Dash callbacks. This is the test class that catches
version drift, `_js_dist`/packaging regressions, and bundle-loading breakage.

Requires a browser (chromedriver on PATH + selenium >= 4); opt in with:
    DECKGL_BROWSER_TESTS=1 poetry run pytest tests/test_integration_smoke.py --headless
CI sets the env var (GitHub runners ship Chrome + chromedriver).
"""
import json
import os
import time

import pytest
from dash import Dash, html, Input, Output
from selenium.webdriver.common.action_chains import ActionChains

from deckgl_dash import DeckGL

pytestmark = pytest.mark.skipif(not os.environ.get("DECKGL_BROWSER_TESTS"),
                                reason = "browser test; set DECKGL_BROWSER_TESTS=1 (needs chromedriver + selenium>=4)")

VIEW = {"longitude": -122.43, "latitude": 37.78, "zoom": 12}
GEOJSON = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-122.43, 37.78]}, "properties": {"name": "center-point"}},
]}


def test_component_mounts_and_events_round_trip(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("swap-data", id = "swap"),
        html.Div(id = "click-out"),
        html.Div(id = "swap-out"),
        DeckGL(
            id = "map",
            initial_view_state = VIEW,
            enable_events = ["click"],
            style = {"width": "500px", "height": "400px", "position": "relative"},
            layers = [
                {"@@type": "TileLayer", "id": "basemap", "data": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                 "minZoom": 0, "maxZoom": 19, "tileSize": 256},
                {"@@type": "GeoJsonLayer", "id": "features", "data": GEOJSON, "pickable": True,
                 "pointRadiusMinPixels": 12, "getFillColor": [255, 0, 0]},
            ],
        ),
    ])

    @app.callback(Output("click-out", "children"), Input("map", "clickInfo"))
    def on_click(info):
        return json.dumps(info) if info else "none"

    @app.callback(Output("map", "layerData"), Output("swap-out", "children"), Input("swap", "n_clicks"), prevent_initial_call = True)
    def swap_data(n):
        return {"features": GEOJSON}, f"swapped-{n}"

    dash_duo.start_server(app)

    # 1. Component mounts: the deck.gl canvas exists (catches _js_dist/bundle regressions)
    dash_duo.wait_for_element("#map canvas", timeout = 15)
    time.sleep(3)  # allow layers to build and render

    # 2. clickInfo round-trips: click the feature at view center
    canvas = dash_duo.driver.find_element("css selector", "#map canvas")
    ActionChains(dash_duo.driver).move_to_element(canvas).click().perform()
    dash_duo.wait_for_contains_text("#click-out", "center-point", timeout = 10)
    info = json.loads(dash_duo.find_element("#click-out").text)
    assert info["picked"] is True
    assert info["layerId"] == "features"

    # 3. layer_data round-trips without crashing the component
    dash_duo.find_element("#swap").click()
    dash_duo.wait_for_text_to_equal("#swap-out", "swapped-1", timeout = 10)
    time.sleep(1)
    assert dash_duo.driver.execute_script("return document.querySelectorAll('#map canvas').length") >= 1
