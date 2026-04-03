# Layer Ordering

## How Layer Order Works

deck.gl renders layers in array order: the first layer in the `layers` list is drawn at the bottom, and the last is drawn on top. This means that if you have a polygon layer followed by a point layer, the points will be visible on top of the polygons.

```python
DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', ...),        # bottom
        GeoJsonLayer(id='polygons', ...),     # middle
        ScatterplotLayer(id='points', ...),   # top
    ],
)
```

## The Problem

To reorder layers, you would normally need to rebuild and resend the entire `layers` array — including all the data for every layer. For large datasets, this is expensive and unnecessary when only the draw order is changing.

## The Solution: `layer_order`

The `layer_order` prop accepts a list of layer IDs that defines the rendering order from bottom to top. It reorders layers on the client without resending any data:

```python
DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        GeoJsonLayer(id='polygons', data=polygon_data, get_fill_color='#FF8C00'),
        ScatterplotLayer(id='points', data=point_data, get_position='@@=coordinates'),
    ],
    layer_order=['basemap', 'polygons', 'points'],  # explicit order
)
```

## Dynamic Reordering

Use a Dash callback to reorder layers at runtime:

```python
from dash import Dash, html, dcc, callback, Output, Input
from deckgl_dash import DeckGL
from deckgl_dash.layers import TileLayer, GeoJsonLayer, ScatterplotLayer

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='order-dropdown',
        options=[
            {'label': 'Points on top', 'value': 'points-on-top'},
            {'label': 'Polygons on top', 'value': 'polygons-on-top'},
        ],
        value='points-on-top',
    ),
    DeckGL(
        id='map',
        layers=[
            TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
            GeoJsonLayer(id='polygons', data=polygon_data, get_fill_color='#FF8C00'),
            ScatterplotLayer(id='points', data=point_data, get_position='@@=coordinates'),
        ],
        initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11},
    ),
])


@callback(Output('map', 'layerOrder'), Input('order-dropdown', 'value'))
def reorder_layers(value):
    if value == 'points-on-top':
        return ['basemap', 'polygons', 'points']
    return ['basemap', 'points', 'polygons']
```

## Resetting to Default Order

Set `layer_order` to an empty list to revert to the original array order:

```python
@callback(Output('map', 'layerOrder'), Input('reset-btn', 'n_clicks'), prevent_initial_call=True)
def reset_order(n):
    return []  # reverts to original layers array order
```

## Combining with `layer_data`

`layer_order` and `layer_data` are independent props. You can update layer data and reorder layers in separate callbacks without conflicts:

```python
# One callback updates data
@callback(Output('map', 'layerData'), Input('load-btn', 'n_clicks'), prevent_initial_call=True)
def load_data(n):
    return {'points': generate_new_points()}


# Another callback reorders layers
@callback(Output('map', 'layerOrder'), Input('order-dropdown', 'value'))
def reorder(value):
    if value == 'points-on-top':
        return ['basemap', 'polygons', 'points']
    return ['basemap', 'points', 'polygons']
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| `layer_order` is `None` or `[]` | Layers render in their original array order |
| ID in `layer_order` not in `layers` | Silently skipped |
| Layer ID not in `layer_order` | Appended at the top (rendered last) |
| Duplicate IDs in `layer_order` | First occurrence wins |

## When to Use `layers` vs `layer_order`

| Scenario | Use |
|----------|-----|
| Adding/removing layers | `layers` |
| Changing layer styling | `layers` |
| Changing the rendering order | `layer_order` |
| Updating layer data | `layer_data` |
