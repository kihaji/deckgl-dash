"""Python layer helpers for deckgl-dash.

Provides Pythonic layer classes that serialize to deck.gl JSON format.
Supports snake_case properties, hex color strings, and @@= accessor syntax.

Example:
    >>> from deckgl_dash.layers import TileLayer, GeoJsonLayer
    >>>
    >>> DeckGL(
    ...     id='map',
    ...     layers=[
    ...         TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
    ...         GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True)
    ...     ],
    ...     initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
    ... )
"""
from .base import BaseLayer, process_layers, normalize_color, to_camel_case

# Core layers (@deck.gl/layers)
from .core import (
    GeoJsonLayer,
    ScatterplotLayer,
    PathLayer,
    LineLayer,
    ArcLayer,
    IconLayer,
    TextLayer,
    PolygonLayer,
)

# Geo layers (@deck.gl/geo-layers)
from .geo import (
    TileLayer,
    MVTLayer,
    BitmapLayer,
)

# Aggregation layers (@deck.gl/aggregation-layers)
from .aggregation import (
    HeatmapLayer,
    HexagonLayer,
    GridLayer,
)

__all__ = [
    # Base
    'BaseLayer',
    'process_layers',
    'normalize_color',
    'to_camel_case',
    # Core layers
    'GeoJsonLayer',
    'ScatterplotLayer',
    'PathLayer',
    'LineLayer',
    'ArcLayer',
    'IconLayer',
    'TextLayer',
    'PolygonLayer',
    # Geo layers
    'TileLayer',
    'MVTLayer',
    'BitmapLayer',
    # Aggregation layers
    'HeatmapLayer',
    'HexagonLayer',
    'GridLayer',
]
