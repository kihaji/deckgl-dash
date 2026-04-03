"""Drawing demo - Interactive drawing on the map.

Demonstrates drawing lines, circles, rectangles, and polygons using the
DrawingConfig and DrawingStyle helpers.
"""
import json
from dash import Dash, html, Input, Output, State, callback_context, no_update
from deckgl_dash import DeckGL, DrawingConfig, DrawingStyle, EMPTY_FEATURE_COLLECTION
from deckgl_dash.layers import TileLayer

app = Dash(__name__)

BASEMAP = TileLayer(id = 'basemap', data = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', min_zoom = 0, max_zoom = 19)

DRAW_STYLE = DrawingStyle(
    fill_color = [255, 140, 0, 100],
    line_color = '#333333',
    line_width = 2,
    tentative_fill_color = [255, 140, 0, 50],
    tentative_line_color = '#FF8C00',
)

BUTTON_STYLE = {'padding': '8px 16px', 'margin': '4px', 'cursor': 'pointer', 'border': '1px solid #ccc', 'borderRadius': '4px', 'backgroundColor': '#fff'}
DELETE_STYLE = {'padding': '8px 16px', 'margin': '4px', 'cursor': 'pointer', 'border': '1px solid #c00', 'borderRadius': '4px', 'backgroundColor': '#fff', 'color': '#c00'}

app.layout = html.Div([
    html.H2("Drawing Demo"),
    html.Div([
        html.Button("Polygon", id = "btn-polygon", style = BUTTON_STYLE),
        html.Button("Line", id = "btn-line", style = BUTTON_STYLE),
        html.Button("Circle", id = "btn-circle", style = BUTTON_STYLE),
        html.Button("Rectangle", id = "btn-rectangle", style = BUTTON_STYLE),
        html.Button("Square", id = "btn-square", style = BUTTON_STYLE),
        html.Button("Point", id = "btn-point", style = BUTTON_STYLE),
        html.Button("Modify", id = "btn-modify", style = BUTTON_STYLE),
        html.Button("Delete Selected", id = "btn-delete", style = DELETE_STYLE),
        html.Button("Clear All", id = "btn-clear", style = DELETE_STYLE),
    ], style = {'marginBottom': '10px'}),
    html.Div(id = 'mode-display', style = {'marginBottom': '10px', 'fontWeight': 'bold'}),
    DeckGL(
        id = 'map',
        layers = [BASEMAP],
        drawing_config = DrawingConfig(mode = 'draw_polygon', style = DRAW_STYLE),
        drawing_features = EMPTY_FEATURE_COLLECTION,
        initial_view_state = {'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
        style = {'height': '600px'},
    ),
    html.H4("Drawn Features (GeoJSON):"),
    html.Pre(id = 'feature-output', style = {'maxHeight': '300px', 'overflow': 'auto', 'backgroundColor': '#f5f5f5', 'padding': '10px', 'borderRadius': '4px'}),
])

MODE_MAP = {
    'btn-polygon': 'draw_polygon',
    'btn-line': 'draw_line',
    'btn-circle': 'draw_circle',
    'btn-rectangle': 'draw_rectangle',
    'btn-square': 'draw_square',
    'btn-point': 'draw_point',
    'btn-modify': 'modify',
}


@app.callback(
    Output('map', 'drawingConfig'),
    Output('map', 'drawingFeatures'),
    Output('mode-display', 'children'),
    [Input(btn_id, 'n_clicks') for btn_id in [*MODE_MAP.keys(), 'btn-delete', 'btn-clear']],
    State('map', 'drawingConfig'),
    prevent_initial_call = True,
)
def set_draw_mode(*args):
    btn = str(callback_context.triggered_id)
    current_config = args[-1] or {}
    if btn == 'btn-clear':
        return DrawingConfig(mode = 'view', style = DRAW_STYLE).to_dict(), EMPTY_FEATURE_COLLECTION, "Mode: view (cleared)"
    if btn == 'btn-delete':
        # Trigger delete of selected feature(s) — stays in current mode
        return {**current_config, 'deleteSelected': True}, no_update, "Deleting selected..."
    mode = MODE_MAP.get(btn, 'view')
    return DrawingConfig(mode = mode, style = DRAW_STYLE).to_dict(), no_update, f"Mode: {mode}"


@app.callback(
    Output('feature-output', 'children'),
    Input('map', 'drawingFeatures'),
)
def display_features(fc):
    if not fc or not fc.get('features'):
        return "No features drawn yet."
    return json.dumps(fc, indent = 2)


if __name__ == '__main__':
    app.run(debug = True)
