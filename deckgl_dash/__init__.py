"""deckgl-dash: Direct deck.gl wrapper for Plotly Dash.

High-performance WebGL-powered visualization with support for large vector datasets,
Cloud Optimized GeoTIFFs (COGs), and tile-based base maps.

Example:
    >>> from dash import Dash
    >>> from deckgl_dash import DeckGL
    >>> from deckgl_dash.layers import TileLayer, GeoJsonLayer
    >>>
    >>> app = Dash(__name__)
    >>> app.layout = DeckGL(
    ...     id='map',
    ...     layers=[
    ...         TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
    ...         GeoJsonLayer(id='data', data=geojson, get_fill_color='#FF8C00', pickable=True)
    ...     ],
    ...     initial_view_state={'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}
    ... )
"""
from __future__ import print_function as _

import os as _os
import sys as _sys
import json

import dash as _dash

# Import the wrapped DeckGL component (supports Python layer helpers)
# Import DeckGLBase from component.py (not .DeckGL) to prevent Pyright from
# shadowing the DeckGL class with the DeckGL.py module name.
from .component import DeckGL as DeckGL
from .component import DeckGLBase as DeckGLBase

# Import layers module for convenience
from . import layers

# Import maplibre module for MapLibre GL JS integration
from . import maplibre

# Import color scale utilities
from .colors import ColorScale, color_range_from_scale, AVAILABLE_SCALES

# Export list
__all__ = ['DeckGL', 'DeckGLBase', 'layers', 'maplibre', 'ColorScale', 'color_range_from_scale', 'AVAILABLE_SCALES']

if not hasattr(_dash, '__plotly_dash') and not hasattr(_dash, 'development'):
    print('Dash was not successfully imported. '
          'Make sure you don\'t have a file '
          'named \n"dash.py" in your current directory.', file=_sys.stderr)
    _sys.exit(1)

_basepath = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_basepath, 'package-info.json'))
with open(_filepath) as f:
    package = json.load(f)

package_name = package['name'].replace(' ', '_').replace('-', '_')
__version__ = package['version']

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_this_module = _sys.modules[__name__]

async_resources = []

_js_dist = []

_js_dist.extend(
    [
        {
            "relative_package_path": "async-{}.js".format(async_resource),
            "external_url": (
                "https://unpkg.com/{0}@{2}"
                "/{1}/async-{3}.js"
            ).format(package_name, __name__, __version__, async_resource),
            "namespace": package_name,
            "async": True,
        }
        for async_resource in async_resources
    ]
)

# TODO: Figure out if unpkg link works
_js_dist.extend(
    [
        {
            "relative_package_path": "async-{}.js.map".format(async_resource),
            "external_url": (
                "https://unpkg.com/{0}@{2}"
                "/{1}/async-{3}.js.map"
            ).format(package_name, __name__, __version__, async_resource),
            "namespace": package_name,
            "dynamic": True,
        }
        for async_resource in async_resources
    ]
)

_js_dist.extend(
    [
        {
            'relative_package_path': 'deckgl_dash.min.js',
            'namespace': package_name
        },
        {
            'relative_package_path': 'deckgl_dash.min.js.map',
            'namespace': package_name,
            'dynamic': True
        }
    ]
)

_css_dist = []

# Set JS/CSS dist for both DeckGL and DeckGLBase
# These are standard Dash component class attributes for asset registration
DeckGL._js_dist = _js_dist  # type: ignore[attr-defined]
DeckGL._css_dist = _css_dist  # type: ignore[attr-defined]
DeckGLBase._js_dist = _js_dist  # type: ignore[attr-defined]
DeckGLBase._css_dist = _css_dist  # type: ignore[attr-defined]
