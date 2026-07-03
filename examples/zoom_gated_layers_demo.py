"""
Demo of zoom-gated layer visibility (visible_min_zoom / visible_max_zoom).

LOD-style dashboards: region polygons show when zoomed out, individual points
appear only past zoom 10. Gating folds into deck.gl `visible` client-side —
crossing a threshold flips layers with no server round trip and no per-frame
churn (layers are only re-pushed when a gate actually flips).
"""
from dash import Dash, html
from deckgl_dash import DeckGL

REGION = {"type": "FeatureCollection", "features": [{
    "type": "Feature",
    "geometry": {"type": "Polygon", "coordinates": [[[-122.52, 37.70], [-122.35, 37.70], [-122.35, 37.84], [-122.52, 37.84], [-122.52, 37.70]]]},
    "properties": {"name": "SF"},
}]}
POINTS = [{"pos": [-122.42 + 0.01 * i, 37.76 + 0.005 * i], "n": i} for i in range(10)]

app = Dash(__name__)
app.layout = html.Div([
    html.H3("Zoom-gated layers: polygon fades out past zoom 10, points fade in"),
    html.P("Zoom in past 10 — the region outline disappears and the points appear."),
    DeckGL(
        id = "map",
        initial_view_state = {"longitude": -122.43, "latitude": 37.77, "zoom": 9},
        style = {"width": "100%", "height": "600px", "position": "relative"},
        layers = [
            {"@@type": "TileLayer", "id": "basemap", "data": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
             "minZoom": 0, "maxZoom": 19, "tileSize": 256},
            # Region overview: only while zoomed OUT (<= 10)
            {"@@type": "GeoJsonLayer", "id": "region", "data": REGION, "stroked": True, "filled": True,
             "getFillColor": [80, 120, 255, 60], "getLineColor": [40, 60, 200], "getLineWidth": 3,
             "lineWidthMinPixels": 2, "visibleMaxZoom": 10},
            # Individual points: only when zoomed IN (>= 10)
            {"@@type": "ScatterplotLayer", "id": "points", "data": POINTS, "getPosition": "@@=pos",
             "getRadius": 60, "radiusMinPixels": 5, "getFillColor": [220, 40, 40], "visibleMinZoom": 10},
        ],
    ),
])

if __name__ == "__main__":
    app.run(debug = True, port = 8057)
