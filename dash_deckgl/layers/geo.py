"""Geo layer helpers for dash-deckgl (from @deck.gl/geo-layers)."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from .base import BaseLayer, AccessorValue, ColorValue


class TileLayer(BaseLayer):
    """Render tiled data (raster or vector) from a tile server.

    Supports XYZ tile URLs with {x}, {y}, {z} placeholders. Automatically configures
    raster tile rendering for common tile servers (OSM, CARTO, etc.).

    Example:
        >>> TileLayer(
        ...     id='basemap',
        ...     data='https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ...     min_zoom=0,
        ...     max_zoom=19
        ... )
    """
    _layer_type = 'TileLayer'
    _color_props = ()
    _accessor_props = ()

    def __init__(
        self, id: str, data: str, *,
        # Tile settings
        tile_size: Optional[int] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        max_cache_size: Optional[int] = None,
        max_cache_byte_size: Optional[int] = None,
        refinement_strategy: Optional[str] = None,  # 'best-available' | 'no-overlap' | 'never'
        z_range: Optional[List[int]] = None,
        # Extent/bounds
        extent: Optional[List[float]] = None,  # [minX, minY, maxX, maxY]
        # Loading
        max_requests: Optional[int] = None,
        # Rendering (for sublayers)
        render_sublayers: Optional[Any] = None,  # Function - typically not used from Python
        # Interaction
        pickable: Optional[bool] = None,
        auto_highlight: Optional[bool] = None,
        highlight_color: Optional[ColorValue] = None,
        # Other
        opacity: Optional[float] = None,
        visible: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(id)
        self._set_prop('data', data)
        # Tile settings
        self._set_prop('tile_size', tile_size)
        self._set_prop('min_zoom', min_zoom)
        self._set_prop('max_zoom', max_zoom)
        self._set_prop('max_cache_size', max_cache_size)
        self._set_prop('max_cache_byte_size', max_cache_byte_size)
        self._set_prop('refinement_strategy', refinement_strategy)
        self._set_prop('z_range', z_range)
        # Extent
        self._set_prop('extent', extent)
        # Loading
        self._set_prop('max_requests', max_requests)
        # Rendering
        self._set_prop('render_sublayers', render_sublayers)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class MVTLayer(BaseLayer):
    """Render Mapbox Vector Tiles (MVT) with styling.

    Example:
        >>> MVTLayer(
        ...     id='vector-tiles',
        ...     data='https://tiles.example.com/{z}/{x}/{y}.mvt',
        ...     get_fill_color='@@=properties.color',
        ...     get_line_color=[0, 0, 0],
        ...     get_line_width=1,
        ...     pickable=True
        ... )
    """
    _layer_type = 'MVTLayer'
    _color_props = ('get_fill_color', 'get_line_color', 'get_point_color')
    _accessor_props = ('get_fill_color', 'get_line_color', 'get_line_width', 'get_point_radius', 'get_elevation')

    def __init__(
        self, id: str, data: str, *,
        # Tile settings
        tile_size: Optional[int] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        max_cache_size: Optional[int] = None,
        max_cache_byte_size: Optional[int] = None,
        refinement_strategy: Optional[str] = None,
        extent: Optional[List[float]] = None,
        # Unique key for features
        unique_id_property: Optional[str] = None,
        highlighted_feature_id: Optional[Any] = None,
        # Rendering options
        filled: Optional[bool] = None,
        stroked: Optional[bool] = None,
        extruded: Optional[bool] = None,
        wireframe: Optional[bool] = None,
        # Point options
        point_type: Optional[str] = None,
        # Style accessors
        get_fill_color: Optional[AccessorValue] = None,
        get_line_color: Optional[AccessorValue] = None,
        get_line_width: Optional[AccessorValue] = None,
        get_point_radius: Optional[AccessorValue] = None,
        get_elevation: Optional[AccessorValue] = None,
        # Size scales
        line_width_units: Optional[str] = None,
        line_width_scale: Optional[float] = None,
        line_width_min_pixels: Optional[float] = None,
        line_width_max_pixels: Optional[float] = None,
        point_radius_units: Optional[str] = None,
        point_radius_scale: Optional[float] = None,
        point_radius_min_pixels: Optional[float] = None,
        point_radius_max_pixels: Optional[float] = None,
        elevation_scale: Optional[float] = None,
        # Binary mode (performance)
        binary: Optional[bool] = None,
        # Interaction
        pickable: Optional[bool] = None,
        auto_highlight: Optional[bool] = None,
        highlight_color: Optional[ColorValue] = None,
        # Other
        opacity: Optional[float] = None,
        visible: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(id)
        self._set_prop('data', data)
        # Tile settings
        self._set_prop('tile_size', tile_size)
        self._set_prop('min_zoom', min_zoom)
        self._set_prop('max_zoom', max_zoom)
        self._set_prop('max_cache_size', max_cache_size)
        self._set_prop('max_cache_byte_size', max_cache_byte_size)
        self._set_prop('refinement_strategy', refinement_strategy)
        self._set_prop('extent', extent)
        # Feature key
        self._set_prop('unique_id_property', unique_id_property)
        self._set_prop('highlighted_feature_id', highlighted_feature_id)
        # Rendering
        self._set_prop('filled', filled)
        self._set_prop('stroked', stroked)
        self._set_prop('extruded', extruded)
        self._set_prop('wireframe', wireframe)
        self._set_prop('point_type', point_type)
        # Style
        self._set_prop('get_fill_color', get_fill_color)
        self._set_prop('get_line_color', get_line_color)
        self._set_prop('get_line_width', get_line_width)
        self._set_prop('get_point_radius', get_point_radius)
        self._set_prop('get_elevation', get_elevation)
        # Size scales
        self._set_prop('line_width_units', line_width_units)
        self._set_prop('line_width_scale', line_width_scale)
        self._set_prop('line_width_min_pixels', line_width_min_pixels)
        self._set_prop('line_width_max_pixels', line_width_max_pixels)
        self._set_prop('point_radius_units', point_radius_units)
        self._set_prop('point_radius_scale', point_radius_scale)
        self._set_prop('point_radius_min_pixels', point_radius_min_pixels)
        self._set_prop('point_radius_max_pixels', point_radius_max_pixels)
        self._set_prop('elevation_scale', elevation_scale)
        # Binary
        self._set_prop('binary', binary)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class BitmapLayer(BaseLayer):
    """Render a bitmap image at specified bounds.

    Example:
        >>> BitmapLayer(
        ...     id='satellite',
        ...     image='https://example.com/image.png',
        ...     bounds=[-122.5, 37.5, -122.0, 38.0]  # [west, south, east, north]
        ... )
    """
    _layer_type = 'BitmapLayer'
    _color_props = ('tint_color',)
    _accessor_props = ()

    def __init__(
        self, id: str, *,
        # Image source
        image: Optional[str] = None,
        bounds: Optional[List[float]] = None,  # [west, south, east, north] or [[west, south], [east, north]]
        # Loading
        load_options: Optional[Dict[str, Any]] = None,
        # Rendering
        tint_color: Optional[ColorValue] = None,
        desaturate: Optional[float] = None,  # 0-1
        transparent_color: Optional[ColorValue] = None,
        texture_parameters: Optional[Dict[str, Any]] = None,
        # Interaction
        pickable: Optional[bool] = None,
        auto_highlight: Optional[bool] = None,
        highlight_color: Optional[ColorValue] = None,
        # Other
        opacity: Optional[float] = None,
        visible: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(id)
        self._set_prop('image', image)
        self._set_prop('bounds', bounds)
        # Loading
        self._set_prop('load_options', load_options)
        # Rendering
        self._set_prop('tint_color', tint_color)
        self._set_prop('desaturate', desaturate)
        self._set_prop('transparent_color', transparent_color)
        self._set_prop('texture_parameters', texture_parameters)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)
