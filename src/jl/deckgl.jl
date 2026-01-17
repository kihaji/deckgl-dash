# AUTO GENERATED FILE - DO NOT EDIT

export deckgl

"""
    deckgl(;kwargs...)

A DeckGL component.
DeckGL component for Plotly Dash
A high-performance WebGL-powered visualization component wrapping deck.gl
Supports all deck.gl layer types via JSON configuration
Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `clickInfo` (Dict; optional): (Output) Information about the last clicked feature.
Updated when click events are enabled.
- `controller` (Bool | Dict; optional): Enable map interactions. Can be:
- true: Enable all default interactions
- false: Disable all interactions
- object: Fine-grained control (e.g., {dragPan: true, scrollZoom: false})
- `enableEvents` (Bool | Array of Strings; optional): Enable events for Dash callbacks. Events are disabled by default for performance.
Can be:
- false: No events (default)
- true: Enable all events (click, hover, viewStateChange)
- array: Enable specific events, e.g., ['click', 'hover']
- `hoverInfo` (Dict; optional): (Output) Information about the currently hovered feature.
Updated when hover events are enabled.
- `initialViewState` (optional): Initial view state for uncontrolled mode. Sets the initial camera position.
Properties: longitude, latitude, zoom, pitch, bearing. initialViewState has the following type: lists containing elements 'longitude', 'latitude', 'zoom', 'pitch', 'bearing'.
Those elements have the following types:
  - `longitude` (Real; optional)
  - `latitude` (Real; optional)
  - `zoom` (Real; optional)
  - `pitch` (Real; optional)
  - `bearing` (Real; optional)
- `layers` (Array of Dicts; optional): Array of layer configurations. Each layer should have a '@@type' property
specifying the layer type (e.g., 'GeoJsonLayer', 'TileLayer').
Supports all deck.gl layer types.
- `style` (Dict; optional): CSS styles for the container div.
Default height is 400px if not specified.
- `tooltip` (Bool | Dict; optional): Tooltip configuration. Can be:
- false: No tooltip (default)
- true: Show all properties on hover
- object: {html: "template with {property}", style: {}}
- `viewState` (optional): Controlled view state. When provided, the component operates in controlled mode
and this prop fully controls the camera position.. viewState has the following type: lists containing elements 'longitude', 'latitude', 'zoom', 'pitch', 'bearing'.
Those elements have the following types:
  - `longitude` (Real; optional)
  - `latitude` (Real; optional)
  - `zoom` (Real; optional)
  - `pitch` (Real; optional)
  - `bearing` (Real; optional)
"""
function deckgl(; kwargs...)
        available_props = Symbol[:id, :clickInfo, :controller, :enableEvents, :hoverInfo, :initialViewState, :layers, :style, :tooltip, :viewState]
        wild_props = Symbol[]
        return Component("deckgl", "DeckGL", "dash_deckgl", available_props, wild_props; kwargs...)
end

