"""
Demo of dynamically switching MapLibre basemap styles while preserving view state.

This example demonstrates the CORRECT pattern for basemap switching:
- Update only the `maplibre_config` prop on an existing DeckGL component
- The map preserves the user's current pan/zoom/pitch/bearing across style changes
- Do NOT recreate the entire DeckGL component (see maplibre_vector_demo.py for the old pattern)
"""
from dash import Dash, html, dcc, callback, Output, Input
import json

from deckgl_dash import DeckGL
from deckgl_dash.layers import GeoJsonLayer
from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle

# Sample GeoJSON overlay data
SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Mission District", "population": 60000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.428, 37.755], [-122.406, 37.755], [-122.406, 37.765],
                    [-122.428, 37.765], [-122.428, 37.755],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "Castro", "population": 20000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.445, 37.755], [-122.428, 37.755], [-122.428, 37.765],
                    [-122.445, 37.765], [-122.445, 37.755],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"name": "SoMa", "population": 45000},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.415, 37.770], [-122.395, 37.770], [-122.395, 37.785],
                    [-122.415, 37.785], [-122.415, 37.770],
                ]],
            },
        },
    ],
}

STYLE_OPTIONS = {
    "carto-positron": {"label": "CARTO Positron", "url": MapLibreStyle.CARTO_POSITRON},
    "carto-dark": {"label": "CARTO Dark Matter", "url": MapLibreStyle.CARTO_DARK_MATTER},
    "carto-voyager": {"label": "CARTO Voyager", "url": MapLibreStyle.CARTO_VOYAGER},
    "ofm-liberty": {"label": "OpenFreeMap Liberty", "url": MapLibreStyle.OPENFREEMAP_LIBERTY},
    "ofm-bright": {"label": "OpenFreeMap Bright", "url": MapLibreStyle.OPENFREEMAP_BRIGHT},
    "ofm-positron": {"label": "OpenFreeMap Positron", "url": MapLibreStyle.OPENFREEMAP_POSITRON},
}

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Basemap Style Switching Demo"),
    html.P(
        "Pan/zoom the map, then switch styles — the view state is preserved. "
        "Enable viewStateChange events below to see the current camera position."
    ),
    html.Div([
        html.Label("Select basemap style:", style = {"fontWeight": "bold", "marginRight": "10px"}),
        dcc.Dropdown(
            id = "style-dropdown",
            options = [{"label": v["label"], "value": k} for k, v in STYLE_OPTIONS.items()],
            value = "carto-positron",
            clearable = False,
            style = {"width": "300px", "display": "inline-block", "verticalAlign": "middle"},
        ),
    ], style = {"marginBottom": "10px"}),
    # The DeckGL component is created ONCE — only maplibre_config is updated by the callback
    DeckGL(
        id = "map",
        maplibre_config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON).to_dict(),
        layers = [
            GeoJsonLayer(
                id = "neighborhoods",
                data = SAMPLE_GEOJSON,
                filled = True,
                stroked = True,
                get_fill_color = [255, 87, 34, 120],
                get_line_color = "#000000",
                get_line_width = 2,
                line_width_min_pixels = 1,
                pickable = True,
                auto_highlight = True,
                highlight_color = [255, 255, 0, 100],
                opacity = 0.6,
            ),
        ],
        initial_view_state = {
            "longitude": -122.42,
            "latitude": 37.76,
            "zoom": 12,
            "pitch": 0,
            "bearing": 0,
        },
        enable_events = ["viewStateChange"],
        tooltip = True,
        style = {"width": "100%", "height": "600px"},
    ),
    html.Div([
        html.H4("Current View State:"),
        html.Pre(id = "view-state-output", style = {"backgroundColor": "#f5f5f5", "padding": "10px"}),
    ]),
])


@callback(Output("map", "maplibreConfig"), Input("style-dropdown", "value"))
def switch_basemap(style_key):
    """Update only the maplibre_config prop — the component is NOT recreated."""
    style_url = STYLE_OPTIONS.get(style_key, STYLE_OPTIONS["carto-positron"])["url"]
    return MapLibreConfig(style = style_url).to_dict()


@callback(Output("view-state-output", "children"), Input("map", "viewState"))
def display_view_state(view_state):
    if view_state is None:
        return "Move the map to see view state..."
    return json.dumps(view_state, indent = 2)


if __name__ == "__main__":
    app.run(debug = True, port = 8056)
