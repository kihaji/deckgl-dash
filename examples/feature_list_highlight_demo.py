"""
List -> click-to-highlight demo for deckgl-dash.

A text list of feature names sits beside the map. Clicking a name highlights the
matching feature (polygon or path) on the map; clicking a feature on the map
highlights the matching list item. Both directions are handled in one callback.

Technique: **accessor-based recolor**. Each feature carries a `properties.selected`
flag; the layer's color accessor is a ternary that paints selected features yellow.
On selection we rebuild only the affected layers' data and push it through the
`layerData` prop (`{layer_id: data}` updates just that layer).

Note on accessors: the `@@=...` expression binder exposes `properties` (and
`coordinates`) in scope, so selectable fields live under `properties` for BOTH the
GeoJsonLayer (regions) and the PathLayer (routes), letting them share one accessor form.

Usage:
    python examples/feature_list_highlight_demo.py
"""
from typing import Any, Dict, List, Optional
from dash import Dash, html, callback, Output, Input, State, ctx, no_update, ALL

from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, GeoJsonLayer, PathLayer

# --- Source data -------------------------------------------------------------
# Region names and route names are intentionally disjoint so a single selected
# name unambiguously belongs to one layer.
REGIONS: List[Dict[str, Any]] = [
    {"name": "Mission", "color": [255, 99, 99], "polygon": [
        [-122.428, 37.755], [-122.406, 37.755], [-122.406, 37.765], [-122.428, 37.765], [-122.428, 37.755]]},
    {"name": "Castro", "color": [99, 99, 255], "polygon": [
        [-122.445, 37.755], [-122.428, 37.755], [-122.428, 37.765], [-122.445, 37.765], [-122.445, 37.755]]},
    {"name": "SoMa", "color": [99, 200, 120], "polygon": [
        [-122.415, 37.770], [-122.395, 37.770], [-122.395, 37.785], [-122.415, 37.785], [-122.415, 37.770]]},
]

ROUTES: List[Dict[str, Any]] = [
    {"name": "Embarcadero Run", "color": [60, 140, 240], "path": [
        [-122.394, 37.795], [-122.398, 37.788], [-122.404, 37.781], [-122.409, 37.775]]},
    {"name": "Market Line", "color": [240, 140, 60], "path": [
        [-122.420, 37.775], [-122.412, 37.778], [-122.404, 37.782], [-122.396, 37.786]]},
]

SELECTED_FILL = [255, 255, 0, 200]  # yellow highlight (referenced in the accessor string)

# Shared color accessor: selected -> yellow, else the feature's own color.
HIGHLIGHT_ACCESSOR = "@@=properties.selected ? [255, 255, 0, 200] : properties.color"

# Button styles
BASE_BTN_STYLE = {"display": "block", "width": "100%", "textAlign": "left",
                  "padding": "6px 10px", "margin": "2px 0", "border": "1px solid #ccc",
                  "background": "#fff", "cursor": "pointer"}
SELECTED_BTN_STYLE = {**BASE_BTN_STYLE, "background": "#ffeb3b", "fontWeight": "bold",
                      "border": "1px solid #fbc02d"}


# --- Pure, testable data builders -------------------------------------------
def build_regions_fc(selected_name: Optional[str] = None) -> Dict[str, Any]:
    """Build the regions FeatureCollection, flagging `selected_name` (if any)."""
    features = [{
        "type": "Feature",
        "properties": {"name": r["name"], "color": r["color"], "selected": r["name"] == selected_name},
        "geometry": {"type": "Polygon", "coordinates": [r["polygon"]]},
    } for r in REGIONS]
    return {"type": "FeatureCollection", "features": features}


def build_routes(selected_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Build the routes path list, flagging `selected_name` (if any)."""
    return [{
        "path": r["path"],
        "properties": {"name": r["name"], "color": r["color"], "selected": r["name"] == selected_name},
    } for r in ROUTES]


def _source_for(kind: str) -> List[Dict[str, Any]]:
    return REGIONS if kind == "region" else ROUTES


# --- App ---------------------------------------------------------------------
app = Dash(__name__)


def _name_list(title: str, kind: str, items: List[Dict[str, Any]]) -> html.Div:
    return html.Div([
        html.H4(title),
        html.Ul([
            html.Li(html.Button(
                item["name"],
                id={"type": "feature-name", "kind": kind, "index": i},
                n_clicks=0,
                style=BASE_BTN_STYLE,
            ), style={"listStyle": "none", "margin": 0, "padding": 0})
            for i, item in enumerate(items)
        ], style={"padding": 0, "margin": 0}),
    ])


app.layout = html.Div([
    html.H1("Click a name to highlight a feature"),
    html.P("Click a Region or Route name to highlight it on the map. Click a feature on "
           "the map to highlight its list item. Click empty map to clear."),
    html.Div([
        html.Div([
            _name_list("Regions", "region", REGIONS),
            _name_list("Routes", "route", ROUTES),
        ], style={"width": "240px", "marginRight": "16px"}),
        html.Div(DeckGL(
            id="map",
            layers=[
                TileLayer(id="osm-tiles", data="https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
                          min_zoom=0, max_zoom=19, tile_size=256),
                GeoJsonLayer(id="regions", data=build_regions_fc(), filled=True, stroked=True,
                             get_fill_color=HIGHLIGHT_ACCESSOR, get_line_color="#333333",
                             get_line_width=2, line_width_min_pixels=1, opacity=0.6,
                             pickable=True, auto_highlight=True),
                PathLayer(id="routes", data=build_routes(), get_path="@@=path",
                          get_color=HIGHLIGHT_ACCESSOR, get_width=6, width_min_pixels=4,
                          cap_rounded=True, joint_rounded=True, pickable=True, auto_highlight=True),
            ],
            initial_view_state={"longitude": -122.41, "latitude": 37.772, "zoom": 12.5, "pitch": 0, "bearing": 0},
            controller=True,
            enable_events=["click"],
            style={"width": "100%", "height": "600px"},
        ), style={"flex": "1"}),
    ], style={"display": "flex"}),
])


@callback(
    Output("map", "layerData"),
    Output({"type": "feature-name", "kind": ALL, "index": ALL}, "style"),
    Input({"type": "feature-name", "kind": ALL, "index": ALL}, "n_clicks"),
    Input("map", "clickInfo"),
    State({"type": "feature-name", "kind": ALL, "index": ALL}, "id"),
    prevent_initial_call=True,
)
def on_select(_name_clicks, click_info, button_ids):
    """Resolve the selected feature name (from a list button OR a map click),
    recolor both layers, and highlight the matching list button."""
    selected_name: Optional[str] = None
    trig = ctx.triggered_id

    if isinstance(trig, dict) and trig.get("type") == "feature-name":
        selected_name = _source_for(trig["kind"])[trig["index"]]["name"]
    elif trig == "map":
        if click_info and click_info.get("picked"):
            props = click_info.get("properties") or {}
            selected_name = props.get("name")
        # else: clicked empty map -> selected_name stays None (clears selection)

    layer_data = {"regions": build_regions_fc(selected_name), "routes": build_routes(selected_name)}

    # One style per button, in the same order Dash provides the matching ids.
    styles = []
    for bid in button_ids:
        name = _source_for(bid["kind"])[bid["index"]]["name"]
        styles.append(SELECTED_BTN_STYLE if name == selected_name else BASE_BTN_STYLE)

    return layer_data, styles


if __name__ == "__main__":
    app.run(debug=True, port=8053)
