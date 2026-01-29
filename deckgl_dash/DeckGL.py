# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DeckGL(Component):
    """A DeckGL component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- clickInfo (dict; optional):
    (Output) Information about the last clicked feature. Updated when
    click events are enabled.

- controller (boolean | dict; default True):
    Enable map interactions. Can be: - True: Enable all default
    interactions - False: Disable all interactions - object:
    Fine-grained control (e.g., {dragPan: True, scrollZoom: False}).

- enableEvents (boolean | list of strings; default False):
    Enable events for Dash callbacks. Events are disabled by default
    for performance. Can be: - False: No events (default) - True:
    Enable all events (click, hover, viewStateChange) - array: Enable
    specific events, e.g., ['click', 'hover'].

- hoverInfo (dict; optional):
    (Output) Information about the currently hovered feature. Updated
    when hover events are enabled.

- initialViewState (dict; default {    longitude: -122.4,    latitude: 37.8,    zoom: 11,    pitch: 0,    bearing: 0,}):
    Initial view state for uncontrolled mode. Sets the initial camera
    position. Properties: longitude, latitude, zoom, pitch, bearing.

    `initialViewState` is a dict with keys:

    - longitude (number; optional)

    - latitude (number; optional)

    - zoom (number; optional)

    - pitch (number; optional)

    - bearing (number; optional)

- layers (list of dicts; optional):
    Array of layer configurations. Each layer should have a '@@type'
    property specifying the layer type (e.g., 'GeoJsonLayer',
    'TileLayer'). Supports all deck.gl layer types.

- mapStyleLoaded (boolean; optional):
    (Output) Indicates when the MapLibre style has finished loading.
    Useful for knowing when custom sources/layers can be added.

- maplibreConfig (dict; optional):
    MapLibre GL JS configuration. When provided, renders MapLibre as
    the base map with deck.gl layers as overlays via MapboxOverlay.
    Shape: - style: string | object - Style URL or inline MapLibre
    style spec (required) - sources: object - Additional sources {id:
    sourceSpec} - mapLayers: array - Additional MapLibre layers -
    interleaved: bool - Enable deck.gl layer interleaving (default:
    True) - attributionControl: bool - Show attribution control
    (default: True) - mapOptions: object - Additional MapLibre Map
    options.

    `maplibreConfig` is a dict with keys:

    - style (string | dict; optional)

    - sources (dict; optional)

    - mapLayers (list of dicts; optional)

    - interleaved (boolean; optional)

    - attributionControl (boolean; optional)

    - mapOptions (dict; optional)

- tooltip (boolean | dict; default False):
    Tooltip configuration. Can be: - False: No tooltip (default) -
    True: Show all properties on hover - object: {html: \"template
    with {property}\", style: {}}.

- viewState (dict; optional):
    Controlled view state. When provided, the component operates in
    controlled mode and this prop fully controls the camera position.

    `viewState` is a dict with keys:

    - longitude (number; optional)

    - latitude (number; optional)

    - zoom (number; optional)

    - pitch (number; optional)

    - bearing (number; optional)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'deckgl_dash'
    _type = 'DeckGL'
    InitialViewState = TypedDict(
        "InitialViewState",
            {
            "longitude": NotRequired[NumberType],
            "latitude": NotRequired[NumberType],
            "zoom": NotRequired[NumberType],
            "pitch": NotRequired[NumberType],
            "bearing": NotRequired[NumberType]
        }
    )

    ViewState = TypedDict(
        "ViewState",
            {
            "longitude": NotRequired[NumberType],
            "latitude": NotRequired[NumberType],
            "zoom": NotRequired[NumberType],
            "pitch": NotRequired[NumberType],
            "bearing": NotRequired[NumberType]
        }
    )

    MaplibreConfig = TypedDict(
        "MaplibreConfig",
            {
            "style": NotRequired[typing.Union[str, dict]],
            "sources": NotRequired[dict],
            "mapLayers": NotRequired[typing.Sequence[dict]],
            "interleaved": NotRequired[bool],
            "attributionControl": NotRequired[bool],
            "mapOptions": NotRequired[dict]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        layers: typing.Optional[typing.Sequence[dict]] = None,
        initialViewState: typing.Optional["InitialViewState"] = None,
        viewState: typing.Optional["ViewState"] = None,
        controller: typing.Optional[typing.Union[bool, dict]] = None,
        enableEvents: typing.Optional[typing.Union[bool, typing.Sequence[str]]] = None,
        tooltip: typing.Optional[typing.Union[bool, dict]] = None,
        style: typing.Optional[typing.Any] = None,
        maplibreConfig: typing.Optional["MaplibreConfig"] = None,
        mapStyleLoaded: typing.Optional[bool] = None,
        clickInfo: typing.Optional[dict] = None,
        hoverInfo: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'clickInfo', 'controller', 'enableEvents', 'hoverInfo', 'initialViewState', 'layers', 'mapStyleLoaded', 'maplibreConfig', 'style', 'tooltip', 'viewState']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'clickInfo', 'controller', 'enableEvents', 'hoverInfo', 'initialViewState', 'layers', 'mapStyleLoaded', 'maplibreConfig', 'style', 'tooltip', 'viewState']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DeckGL, self).__init__(**args)

setattr(DeckGL, "__init__", _explicitize_args(DeckGL.__init__))
