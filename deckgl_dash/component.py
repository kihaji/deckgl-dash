"""DeckGL component wrapper with layer auto-conversion support."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from .DeckGL import DeckGL as _DeckGLBase
from .layers.base import BaseLayer, process_layers
from .drawing import DrawingConfig

# Re-export the base component so __init__.py doesn't need to import from .DeckGL directly,
# which causes Pyright to shadow the DeckGL class with the DeckGL.py module.
DeckGLBase = _DeckGLBase


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
        layer_data: Per-layer data overrides (dict of {layer_id: data}). Merges with layers prop.
        layer_order: Layer rendering order as a list of layer IDs from bottom to top.
        initial_view_state: Initial view state (longitude, latitude, zoom, pitch, bearing).
        view_state: Controlled view state for programmatic control.
        controller: Enable map interactions (True/False or fine-grained config dict).
        enable_events: Event opt-in (False, True, or list like ['click', 'hover', 'dataLoadError']).
        tooltip: Tooltip config (False, True, or dict with html/style).
        style: CSS styles for the container.
        maplibre_config: MapLibre GL JS configuration for basemap rendering.
        map_style_loaded: (Output) True when MapLibre style has finished loading.
        click_info: (Output) Last clicked feature info.
        hover_info: (Output) Currently hovered feature info.
        data_load_info: (Output) Last successful remote data load info.
        data_load_error: (Output) Last data load error info.
        drawing_config: Drawing/editing configuration (DrawingConfig or dict with mode/style).
        drawing_features: (Input/Output) GeoJSON FeatureCollection of drawn features.
        drawing_event: (Output) Last drawing event info.
    """

    def __init__(
        self,
        id: Optional[Union[str, dict]] = None,
        layers: Optional[Sequence[Union[BaseLayer, Dict[str, Any]]]] = None,
        layer_data: Optional[Dict[str, Any]] = None,
        layer_order: Optional[Sequence[str]] = None,
        initial_view_state: Optional[Dict[str, Any]] = None,
        view_state: Optional[Dict[str, Any]] = None,
        controller: Optional[Union[bool, dict]] = None,
        enable_events: Optional[Union[bool, Sequence[str]]] = None,
        tooltip: Optional[Union[bool, dict]] = None,
        style: Optional[Any] = None,
        maplibre_config: Optional[Dict[str, Any]] = None,
        map_style_loaded: Optional[bool] = None,
        click_info: Optional[dict] = None,
        hover_info: Optional[dict] = None,
        data_load_info: Optional[dict] = None,
        data_load_error: Optional[dict] = None,
        drawing_config: Optional[Union[DrawingConfig, Dict[str, Any]]] = None,
        drawing_features: Optional[Dict[str, Any]] = None,
        drawing_event: Optional[dict] = None,
        **kwargs
    ):
        # Convert layer objects to dicts
        processed_layers = process_layers(layers) if layers is not None else None

        # Serialize DrawingConfig if needed
        if isinstance(drawing_config, DrawingConfig):
            drawing_config = drawing_config.to_dict()

        # Call parent with processed layers
        # Note: Parent uses camelCase prop names internally
        super().__init__(
            id = id,
            layers = processed_layers,
            layerData = layer_data,  # type: ignore[arg-type]  # wrapper accepts Dict[str, Any]; auto-generated type is Dict[str|float|int, Any]
            layerOrder = list(layer_order) if layer_order is not None else None,
            initialViewState = initial_view_state,  # type: ignore[arg-type]  # wrapper accepts Dict[str, Any] for ergonomics
            viewState = view_state,  # type: ignore[arg-type]
            controller = controller,
            enableEvents = enable_events,
            tooltip = tooltip,
            style = style,
            maplibreConfig = maplibre_config,  # type: ignore[arg-type]
            mapStyleLoaded = map_style_loaded,
            clickInfo = click_info,
            hoverInfo = hover_info,
            dataLoadInfo = data_load_info,
            dataLoadError = data_load_error,
            drawingConfig = drawing_config,  # type: ignore[arg-type]  # wrapper accepts Dict[str, Any]; auto-generated type is DrawingConfig
            drawingFeatures = drawing_features,
            drawingEvent = drawing_event,
            **kwargs
        )
