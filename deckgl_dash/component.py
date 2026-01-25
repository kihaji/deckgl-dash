"""DeckGL component wrapper with layer auto-conversion support."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from .DeckGL import DeckGL as _DeckGLBase
from .layers.base import BaseLayer, process_layers


class DeckGL(_DeckGLBase):
    """DeckGL component for Plotly Dash with Python layer helper support.

    A high-performance WebGL-powered visualization component wrapping deck.gl.
    Supports all deck.gl layer types via JSON configuration or Python layer helpers.

    Example with Python helpers:
        >>> from deckgl_dash import DeckGL
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

    Example with JSON/dict:
        >>> DeckGL(
        ...     id='map',
        ...     layers=[{
        ...         '@@type': 'GeoJsonLayer',
        ...         'id': 'geojson',
        ...         'data': 'https://example.com/data.geojson',
        ...         'getFillColor': [255, 140, 0],
        ...         'pickable': True
        ...     }],
        ...     initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
        ... )

    Keyword arguments:
        id: The ID used to identify this component in Dash callbacks.
        layers: Array of layer configurations (BaseLayer objects or dicts with @@type).
        initial_view_state: Initial view state (longitude, latitude, zoom, pitch, bearing).
        view_state: Controlled view state for programmatic control.
        controller: Enable map interactions (True/False or fine-grained config dict).
        enable_events: Event opt-in (False, True, or list like ['click', 'hover']).
        tooltip: Tooltip config (False, True, or dict with html/style).
        style: CSS styles for the container.
        click_info: (Output) Last clicked feature info.
        hover_info: (Output) Currently hovered feature info.
    """

    def __init__(
        self,
        id: Optional[Union[str, dict]] = None,
        layers: Optional[Sequence[Union[BaseLayer, Dict[str, Any]]]] = None,
        initial_view_state: Optional[Dict[str, Any]] = None,
        view_state: Optional[Dict[str, Any]] = None,
        controller: Optional[Union[bool, dict]] = None,
        enable_events: Optional[Union[bool, Sequence[str]]] = None,
        tooltip: Optional[Union[bool, dict]] = None,
        style: Optional[Any] = None,
        click_info: Optional[dict] = None,
        hover_info: Optional[dict] = None,
        **kwargs
    ):
        # Convert layer objects to dicts
        processed_layers = process_layers(layers) if layers is not None else None

        # Call parent with processed layers
        # Note: Parent uses camelCase prop names internally
        super().__init__(
            id = id,
            layers = processed_layers,
            initialViewState = initial_view_state,
            viewState = view_state,
            controller = controller,
            enableEvents = enable_events,
            tooltip = tooltip,
            style = style,
            clickInfo = click_info,
            hoverInfo = hover_info,
            **kwargs
        )
