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

- currentTime (number; optional):
    (Output) The current playback head time T during animation,
    reported ~8 Hz. Use it to drive a slider handle, a time readout,
    or other callbacks.

- dataLoadError (dict; optional):
    (Output) Information about the last data load error. Updated when
    'dataLoadError' is included in enableEvents and a layer fails to
    load data from a URL. Contains: { layerId, error, timestamp }.

- dataLoadInfo (dict; optional):
    (Output) Information about the last successful remote data load.
    Updated when 'dataLoad' is included in enableEvents and a layer
    loads data from a URL. Contains: { layerId, featureCount,
    timestamp }.

- drawingConfig (dict; optional):
    Drawing/editing configuration. When provided with a drawing mode,
    an EditableGeoJsonLayer is added on top of all other layers.
    Shape: - mode: string - Drawing mode ('draw_line', 'draw_polygon',
    'draw_circle',   'draw_rectangle', 'draw_square', 'draw_point',
    'view', 'modify', 'translate') - selectedFeatureIndexes: number[]
    - Indexes of features selected for editing - style: object - Style
    overrides for the editable layer   - fillColor: [r,g,b,a] - Fill
    color for drawn features   - lineColor: [r,g,b,a] - Line/stroke
    color   - lineWidth: number - Line width in pixels   -
    tentativeFillColor: [r,g,b,a] - Fill color while drawing   -
    tentativeLineColor: [r,g,b,a] - Line color while drawing   -
    editHandlePointColor: [r,g,b,a] - Color of vertex edit handles.

    `drawingConfig` is a dict with keys:

    - mode (string; optional)

    - selectedFeatureIndexes (list of numbers; optional)

    - style (dict; optional)

    - deleteSelected (boolean; optional)

- drawingEvent (dict; optional):
    (Output) Information about the last drawing event. Contains: {
    type, featureCount, timestamp }.

- drawingFeatures (dict; optional):
    (Input/Output) GeoJSON FeatureCollection of drawn/edited features.
    Can be set from Python to pre-populate features, and is updated
    from JS when features are added/modified.

- enableEvents (boolean | list of strings; default False):
    Enable events for Dash callbacks. Events are disabled by default
    for performance. Can be: - False: No events (default) - True:
    Enable all events (click, hover, viewStateChange) - array: Enable
    specific events, e.g., ['click', 'hover'].

- fitBounds (dict; optional):
    Fit the camera to a geographic bounding box. Setting this prop
    drives the real camera: MapLibre mode uses the map's native
    `fitBounds`; deck-only mode uses `WebMercatorViewport.fitBounds`
    with the container's real pixel size. Both are viewport-aware, so
    the result frames the bounds tightly.  Shape: - bounds: [[west,
    south], [east, north]] - the box to fit (required) - padding:
    number - pixels of padding around the bounds (default 20) -
    maxZoom: number - clamp the fitted zoom (default 20).

    `fitBounds` is a dict with keys:

    - bounds (list of list of numberss; optional)

    - padding (number; optional)

    - maxZoom (number; optional)

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

- layerData (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Per-layer data overrides. Dict mapping layer IDs to data values.
    Merges with the `layers` prop — only the `data` field of matching
    layers is replaced. Allows updating individual layer data without
    resending the entire layers array.

- layerOrder (list of strings; optional):
    Layer rendering order as an array of layer IDs from bottom to top.
    When provided, layers are reordered to match this sequence without
    resending layer data. Layers not listed are appended at the top.
    Set to an empty array or None to use the original layers array
    order.

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

- timeFilter (dict; optional):
    Time-filter animation config. Drives an internal
    requestAnimationFrame loop that sets each filterable layer's
    `filterRange` on the GPU (via DataFilterExtension) to a sliding
    window `[current - window, current]`. Filtering happens
    client-side at 60fps with no per-frame server round trips; only
    the throttled `currentTime` is reported back.  Target layers are
    those carrying a DataFilterExtension (declare `get_filter_value`
    in Python), or an explicit `layerIds` allowlist. All time values
    must share one scale — keep them float32-safe (e.g. seconds since
    `domain[0]`).  Shape: - domain: [tMin, tMax] - full time extent
    (required for playback) - window: number - sliding-window width in
    time units - current: number - head time T; authoritative while
    paused (slider scrubbing) - playing: bool - run the animation loop
    - speed: number - time units advanced per wall-clock second
    (default: full sweep in ~20s) - loop: bool - wrap the head back to
    `domain[0]+window` at the end (default True) - softEdge: number -
    optional fade width mapped to `filterSoftRange` - layerIds:
    string[] - explicit target layer IDs (default: auto-detect) -
    nonce: number - bump to force a re-sync of an unchanged `current`.

    `timeFilter` is a dict with keys:

    - domain (list of numbers; optional)

    - window (number; optional)

    - current (number; optional)

    - playing (boolean; optional)

    - speed (number; optional)

    - loop (boolean; optional)

    - softEdge (number; optional)

    - layerIds (list of strings; optional)

    - nonce (number; optional)

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

    FitBounds = TypedDict(
        "FitBounds",
            {
            "bounds": NotRequired[typing.Sequence[typing.Sequence[NumberType]]],
            "padding": NotRequired[NumberType],
            "maxZoom": NotRequired[NumberType]
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

    DrawingConfig = TypedDict(
        "DrawingConfig",
            {
            "mode": NotRequired[str],
            "selectedFeatureIndexes": NotRequired[typing.Sequence[NumberType]],
            "style": NotRequired[dict],
            "deleteSelected": NotRequired[bool]
        }
    )

    TimeFilter = TypedDict(
        "TimeFilter",
            {
            "domain": NotRequired[typing.Sequence[NumberType]],
            "window": NotRequired[NumberType],
            "current": NotRequired[NumberType],
            "playing": NotRequired[bool],
            "speed": NotRequired[NumberType],
            "loop": NotRequired[bool],
            "softEdge": NotRequired[NumberType],
            "layerIds": NotRequired[typing.Sequence[str]],
            "nonce": NotRequired[NumberType]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        layers: typing.Optional[typing.Sequence[dict]] = None,
        layerData: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        layerOrder: typing.Optional[typing.Sequence[str]] = None,
        initialViewState: typing.Optional["InitialViewState"] = None,
        viewState: typing.Optional["ViewState"] = None,
        fitBounds: typing.Optional["FitBounds"] = None,
        controller: typing.Optional[typing.Union[bool, dict]] = None,
        enableEvents: typing.Optional[typing.Union[bool, typing.Sequence[str]]] = None,
        tooltip: typing.Optional[typing.Union[bool, dict]] = None,
        style: typing.Optional[typing.Any] = None,
        maplibreConfig: typing.Optional["MaplibreConfig"] = None,
        mapStyleLoaded: typing.Optional[bool] = None,
        clickInfo: typing.Optional[dict] = None,
        hoverInfo: typing.Optional[dict] = None,
        dataLoadInfo: typing.Optional[dict] = None,
        dataLoadError: typing.Optional[dict] = None,
        drawingConfig: typing.Optional["DrawingConfig"] = None,
        drawingFeatures: typing.Optional[dict] = None,
        drawingEvent: typing.Optional[dict] = None,
        timeFilter: typing.Optional["TimeFilter"] = None,
        currentTime: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'clickInfo', 'controller', 'currentTime', 'dataLoadError', 'dataLoadInfo', 'drawingConfig', 'drawingEvent', 'drawingFeatures', 'enableEvents', 'fitBounds', 'hoverInfo', 'initialViewState', 'layerData', 'layerOrder', 'layers', 'mapStyleLoaded', 'maplibreConfig', 'style', 'timeFilter', 'tooltip', 'viewState']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'clickInfo', 'controller', 'currentTime', 'dataLoadError', 'dataLoadInfo', 'drawingConfig', 'drawingEvent', 'drawingFeatures', 'enableEvents', 'fitBounds', 'hoverInfo', 'initialViewState', 'layerData', 'layerOrder', 'layers', 'mapStyleLoaded', 'maplibreConfig', 'style', 'timeFilter', 'tooltip', 'viewState']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DeckGL, self).__init__(**args)

setattr(DeckGL, "__init__", _explicitize_args(DeckGL.__init__))
