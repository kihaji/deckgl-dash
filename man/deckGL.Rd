% Auto-generated: do not edit by hand
\name{deckGL}

\alias{deckGL}

\title{DeckGL component}

\description{
DeckGL component for Plotly Dash A high-performance WebGL-powered visualization component wrapping deck.gl Supports all deck.gl layer types via JSON configuration
}

\usage{
deckGL(id=NULL, clickInfo=NULL, controller=NULL, enableEvents=NULL,
hoverInfo=NULL, initialViewState=NULL, layers=NULL,
style=NULL, tooltip=NULL, viewState=NULL)
}

\arguments{
\item{id}{Character. The ID used to identify this component in Dash callbacks.}

\item{clickInfo}{Named list. (Output) Information about the last clicked feature.
Updated when click events are enabled.}

\item{controller}{Logical | named list. Enable map interactions. Can be:
- true: Enable all default interactions
- false: Disable all interactions
- object: Fine-grained control (e.g., {dragPan: true, scrollZoom: false})}

\item{enableEvents}{Logical | list of characters. Enable events for Dash callbacks. Events are disabled by default for performance.
Can be:
- false: No events (default)
- true: Enable all events (click, hover, viewStateChange)
- array: Enable specific events, e.g., ['click', 'hover']}

\item{hoverInfo}{Named list. (Output) Information about the currently hovered feature.
Updated when hover events are enabled.}

\item{initialViewState}{Lists containing elements 'longitude', 'latitude', 'zoom', 'pitch', 'bearing'.
those elements have the following types:
  - longitude (numeric; optional)
  - latitude (numeric; optional)
  - zoom (numeric; optional)
  - pitch (numeric; optional)
  - bearing (numeric; optional). Initial view state for uncontrolled mode. Sets the initial camera position.
Properties: longitude, latitude, zoom, pitch, bearing}

\item{layers}{List of named lists. Array of layer configurations. Each layer should have a '@@type' property
specifying the layer type (e.g., 'GeoJsonLayer', 'TileLayer').
Supports all deck.gl layer types.}

\item{style}{Named list. CSS styles for the container div.
Default height is 400px if not specified.}

\item{tooltip}{Logical | named list. Tooltip configuration. Can be:
- false: No tooltip (default)
- true: Show all properties on hover
- object: {html: "template with {property}", style: {}}}

\item{viewState}{Lists containing elements 'longitude', 'latitude', 'zoom', 'pitch', 'bearing'.
those elements have the following types:
  - longitude (numeric; optional)
  - latitude (numeric; optional)
  - zoom (numeric; optional)
  - pitch (numeric; optional)
  - bearing (numeric; optional). Controlled view state. When provided, the component operates in controlled mode
and this prop fully controls the camera position.}
}

\value{named list of JSON elements corresponding to React.js properties and their values}

