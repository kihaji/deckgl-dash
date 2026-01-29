"""MapLibre GL JS integration for deckgl-dash.

Provides Python helper classes for configuring MapLibre GL JS basemaps
with deck.gl layer overlays.

Example:
    >>> from deckgl_dash import DeckGL
    >>> from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle
    >>> from deckgl_dash.layers import GeoJsonLayer
    >>>
    >>> DeckGL(
    ...     id='map',
    ...     maplibre_config=MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON).to_dict(),
    ...     layers=[GeoJsonLayer(id='data', data=geojson).to_dict()],
    ... )
"""
from .config import MapLibreConfig, MapLibreStyle
from .sources import RasterSource, VectorSource, GeoJSONSource
from .layers import FillLayer, LineLayer, RasterLayer, CircleLayer, SymbolLayer, FillExtrusionLayer

__all__ = [
    'MapLibreConfig',
    'MapLibreStyle',
    'RasterSource',
    'VectorSource',
    'GeoJSONSource',
    'FillLayer',
    'LineLayer',
    'RasterLayer',
    'CircleLayer',
    'SymbolLayer',
    'FillExtrusionLayer',
]
