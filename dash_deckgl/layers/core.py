"""Core layer helpers for dash-deckgl (from @deck.gl/layers)."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from .base import BaseLayer, AccessorValue, ColorValue


class GeoJsonLayer(BaseLayer):
    """Render GeoJSON features (points, lines, polygons).

    The most versatile layer for vector data. Automatically detects geometry type
    and renders appropriately.

    Example:
        >>> GeoJsonLayer(
        ...     id='geojson',
        ...     data='https://example.com/data.geojson',
        ...     get_fill_color=[255, 140, 0, 200],
        ...     get_line_color='#000000',
        ...     pickable=True
        ... )
    """
    _layer_type = 'GeoJsonLayer'
    _color_props = ('get_fill_color', 'get_line_color', 'get_point_color', 'get_elevation_color')
    _accessor_props = ('get_fill_color', 'get_line_color', 'get_radius', 'get_line_width', 'get_elevation')

    def __init__(
        self, id: str, data: Any, *,
        # Rendering options
        filled: Optional[bool] = None,
        stroked: Optional[bool] = None,
        extruded: Optional[bool] = None,
        wireframe: Optional[bool] = None,
        # Point options
        point_type: Optional[str] = None,  # 'circle', 'icon', 'text', or combination
        # Style accessors
        get_fill_color: Optional[AccessorValue] = None,
        get_line_color: Optional[AccessorValue] = None,
        get_line_width: Optional[AccessorValue] = None,
        get_point_radius: Optional[AccessorValue] = None,
        get_elevation: Optional[AccessorValue] = None,
        # Size scales
        line_width_units: Optional[str] = None,  # 'meters' | 'common' | 'pixels'
        line_width_scale: Optional[float] = None,
        line_width_min_pixels: Optional[float] = None,
        line_width_max_pixels: Optional[float] = None,
        point_radius_units: Optional[str] = None,
        point_radius_scale: Optional[float] = None,
        point_radius_min_pixels: Optional[float] = None,
        point_radius_max_pixels: Optional[float] = None,
        elevation_scale: Optional[float] = None,
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
        # Rendering
        self._set_prop('filled', filled)
        self._set_prop('stroked', stroked)
        self._set_prop('extruded', extruded)
        self._set_prop('wireframe', wireframe)
        self._set_prop('point_type', point_type)
        # Style accessors
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
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class ScatterplotLayer(BaseLayer):
    """Render circles at given coordinates. Optimized for large datasets (millions of points).

    Example:
        >>> ScatterplotLayer(
        ...     id='scatter',
        ...     data=points_data,
        ...     get_position='@@=coordinates',
        ...     get_radius=100,
        ...     get_fill_color=[255, 0, 0],
        ...     pickable=True
        ... )
    """
    _layer_type = 'ScatterplotLayer'
    _color_props = ('get_fill_color', 'get_line_color')
    _accessor_props = ('get_position', 'get_radius', 'get_fill_color', 'get_line_color')

    def __init__(
        self, id: str, data: Any, *,
        # Position accessor
        get_position: Optional[AccessorValue] = None,
        # Rendering
        filled: Optional[bool] = None,
        stroked: Optional[bool] = None,
        # Style accessors
        get_radius: Optional[AccessorValue] = None,
        get_fill_color: Optional[AccessorValue] = None,
        get_line_color: Optional[AccessorValue] = None,
        get_line_width: Optional[AccessorValue] = None,
        # Size scales
        radius_units: Optional[str] = None,  # 'meters' | 'common' | 'pixels'
        radius_scale: Optional[float] = None,
        radius_min_pixels: Optional[float] = None,
        radius_max_pixels: Optional[float] = None,
        line_width_units: Optional[str] = None,
        line_width_scale: Optional[float] = None,
        line_width_min_pixels: Optional[float] = None,
        line_width_max_pixels: Optional[float] = None,
        # Billboard
        billboard: Optional[bool] = None,
        anti_aliasing: Optional[bool] = None,
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
        self._set_prop('get_position', get_position)
        # Rendering
        self._set_prop('filled', filled)
        self._set_prop('stroked', stroked)
        # Style accessors
        self._set_prop('get_radius', get_radius)
        self._set_prop('get_fill_color', get_fill_color)
        self._set_prop('get_line_color', get_line_color)
        self._set_prop('get_line_width', get_line_width)
        # Size scales
        self._set_prop('radius_units', radius_units)
        self._set_prop('radius_scale', radius_scale)
        self._set_prop('radius_min_pixels', radius_min_pixels)
        self._set_prop('radius_max_pixels', radius_max_pixels)
        self._set_prop('line_width_units', line_width_units)
        self._set_prop('line_width_scale', line_width_scale)
        self._set_prop('line_width_min_pixels', line_width_min_pixels)
        self._set_prop('line_width_max_pixels', line_width_max_pixels)
        # Billboard
        self._set_prop('billboard', billboard)
        self._set_prop('anti_aliasing', anti_aliasing)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class PathLayer(BaseLayer):
    """Render paths/polylines from coordinate arrays.

    Example:
        >>> PathLayer(
        ...     id='paths',
        ...     data=routes,
        ...     get_path='@@=coordinates',
        ...     get_color=[0, 100, 200],
        ...     get_width=5,
        ...     pickable=True
        ... )
    """
    _layer_type = 'PathLayer'
    _color_props = ('get_color',)
    _accessor_props = ('get_path', 'get_color', 'get_width')

    def __init__(
        self, id: str, data: Any, *,
        # Path accessor
        get_path: Optional[AccessorValue] = None,
        # Style accessors
        get_color: Optional[AccessorValue] = None,
        get_width: Optional[AccessorValue] = None,
        # Width settings
        width_units: Optional[str] = None,  # 'meters' | 'common' | 'pixels'
        width_scale: Optional[float] = None,
        width_min_pixels: Optional[float] = None,
        width_max_pixels: Optional[float] = None,
        # Rendering
        cap_rounded: Optional[bool] = None,
        joint_rounded: Optional[bool] = None,
        billboard: Optional[bool] = None,
        miter_limit: Optional[float] = None,
        # 3D
        _path_type: Optional[str] = None,  # 'loop' | 'open'
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
        self._set_prop('get_path', get_path)
        # Style accessors
        self._set_prop('get_color', get_color)
        self._set_prop('get_width', get_width)
        # Width settings
        self._set_prop('width_units', width_units)
        self._set_prop('width_scale', width_scale)
        self._set_prop('width_min_pixels', width_min_pixels)
        self._set_prop('width_max_pixels', width_max_pixels)
        # Rendering
        self._set_prop('cap_rounded', cap_rounded)
        self._set_prop('joint_rounded', joint_rounded)
        self._set_prop('billboard', billboard)
        self._set_prop('miter_limit', miter_limit)
        self._set_prop('_path_type', _path_type)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class LineLayer(BaseLayer):
    """Render straight lines between source and target points.

    Example:
        >>> LineLayer(
        ...     id='connections',
        ...     data=connections,
        ...     get_source_position='@@=source',
        ...     get_target_position='@@=target',
        ...     get_color=[100, 100, 100],
        ...     get_width=2
        ... )
    """
    _layer_type = 'LineLayer'
    _color_props = ('get_color',)
    _accessor_props = ('get_source_position', 'get_target_position', 'get_color', 'get_width')

    def __init__(
        self, id: str, data: Any, *,
        # Position accessors
        get_source_position: Optional[AccessorValue] = None,
        get_target_position: Optional[AccessorValue] = None,
        # Style accessors
        get_color: Optional[AccessorValue] = None,
        get_width: Optional[AccessorValue] = None,
        # Width settings
        width_units: Optional[str] = None,
        width_scale: Optional[float] = None,
        width_min_pixels: Optional[float] = None,
        width_max_pixels: Optional[float] = None,
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
        self._set_prop('get_source_position', get_source_position)
        self._set_prop('get_target_position', get_target_position)
        # Style
        self._set_prop('get_color', get_color)
        self._set_prop('get_width', get_width)
        # Width
        self._set_prop('width_units', width_units)
        self._set_prop('width_scale', width_scale)
        self._set_prop('width_min_pixels', width_min_pixels)
        self._set_prop('width_max_pixels', width_max_pixels)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class ArcLayer(BaseLayer):
    """Render raised arcs between source and target points. Great for flow visualization.

    Example:
        >>> ArcLayer(
        ...     id='flights',
        ...     data=flights,
        ...     get_source_position='@@=origin',
        ...     get_target_position='@@=destination',
        ...     get_source_color=[0, 128, 200],
        ...     get_target_color=[200, 0, 80],
        ...     get_width=2
        ... )
    """
    _layer_type = 'ArcLayer'
    _color_props = ('get_source_color', 'get_target_color')
    _accessor_props = ('get_source_position', 'get_target_position', 'get_source_color', 'get_target_color', 'get_width', 'get_height', 'get_tilt')

    def __init__(
        self, id: str, data: Any, *,
        # Position accessors
        get_source_position: Optional[AccessorValue] = None,
        get_target_position: Optional[AccessorValue] = None,
        # Color accessors
        get_source_color: Optional[AccessorValue] = None,
        get_target_color: Optional[AccessorValue] = None,
        # Dimension accessors
        get_width: Optional[AccessorValue] = None,
        get_height: Optional[AccessorValue] = None,
        get_tilt: Optional[AccessorValue] = None,
        # Width settings
        width_units: Optional[str] = None,
        width_scale: Optional[float] = None,
        width_min_pixels: Optional[float] = None,
        width_max_pixels: Optional[float] = None,
        # Arc settings
        great_circle: Optional[bool] = None,
        num_segments: Optional[int] = None,
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
        self._set_prop('get_source_position', get_source_position)
        self._set_prop('get_target_position', get_target_position)
        # Color
        self._set_prop('get_source_color', get_source_color)
        self._set_prop('get_target_color', get_target_color)
        # Dimensions
        self._set_prop('get_width', get_width)
        self._set_prop('get_height', get_height)
        self._set_prop('get_tilt', get_tilt)
        # Width
        self._set_prop('width_units', width_units)
        self._set_prop('width_scale', width_scale)
        self._set_prop('width_min_pixels', width_min_pixels)
        self._set_prop('width_max_pixels', width_max_pixels)
        # Arc
        self._set_prop('great_circle', great_circle)
        self._set_prop('num_segments', num_segments)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class IconLayer(BaseLayer):
    """Render icons/markers at given coordinates.

    Example:
        >>> IconLayer(
        ...     id='markers',
        ...     data=locations,
        ...     get_position='@@=coordinates',
        ...     get_icon='@@=icon',
        ...     icon_atlas='https://example.com/icons.png',
        ...     icon_mapping={'marker': {'x': 0, 'y': 0, 'width': 128, 'height': 128}},
        ...     get_size=40,
        ...     pickable=True
        ... )
    """
    _layer_type = 'IconLayer'
    _color_props = ('get_color',)
    _accessor_props = ('get_position', 'get_icon', 'get_size', 'get_color', 'get_angle', 'get_pixel_offset')

    def __init__(
        self, id: str, data: Any, *,
        # Position
        get_position: Optional[AccessorValue] = None,
        # Icon configuration
        icon_atlas: Optional[str] = None,
        icon_mapping: Optional[Dict[str, Any]] = None,
        get_icon: Optional[AccessorValue] = None,
        # Style accessors
        get_size: Optional[AccessorValue] = None,
        get_color: Optional[AccessorValue] = None,
        get_angle: Optional[AccessorValue] = None,
        get_pixel_offset: Optional[AccessorValue] = None,
        # Size settings
        size_units: Optional[str] = None,
        size_scale: Optional[float] = None,
        size_min_pixels: Optional[float] = None,
        size_max_pixels: Optional[float] = None,
        # Rendering
        billboard: Optional[bool] = None,
        alpha_cutoff: Optional[float] = None,
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
        self._set_prop('get_position', get_position)
        # Icon config
        self._set_prop('icon_atlas', icon_atlas)
        self._set_prop('icon_mapping', icon_mapping)
        self._set_prop('get_icon', get_icon)
        # Style
        self._set_prop('get_size', get_size)
        self._set_prop('get_color', get_color)
        self._set_prop('get_angle', get_angle)
        self._set_prop('get_pixel_offset', get_pixel_offset)
        # Size
        self._set_prop('size_units', size_units)
        self._set_prop('size_scale', size_scale)
        self._set_prop('size_min_pixels', size_min_pixels)
        self._set_prop('size_max_pixels', size_max_pixels)
        # Rendering
        self._set_prop('billboard', billboard)
        self._set_prop('alpha_cutoff', alpha_cutoff)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class TextLayer(BaseLayer):
    """Render text labels at given coordinates.

    Example:
        >>> TextLayer(
        ...     id='labels',
        ...     data=cities,
        ...     get_position='@@=coordinates',
        ...     get_text='@@=name',
        ...     get_size=16,
        ...     get_color=[0, 0, 0],
        ...     get_angle=0,
        ...     pickable=True
        ... )
    """
    _layer_type = 'TextLayer'
    _color_props = ('get_color', 'background_color', 'get_background_color')
    _accessor_props = ('get_position', 'get_text', 'get_size', 'get_color', 'get_angle', 'get_text_anchor', 'get_alignment_baseline', 'get_pixel_offset')

    def __init__(
        self, id: str, data: Any, *,
        # Position & text
        get_position: Optional[AccessorValue] = None,
        get_text: Optional[AccessorValue] = None,
        # Style accessors
        get_size: Optional[AccessorValue] = None,
        get_color: Optional[AccessorValue] = None,
        get_angle: Optional[AccessorValue] = None,
        get_text_anchor: Optional[AccessorValue] = None,
        get_alignment_baseline: Optional[AccessorValue] = None,
        get_pixel_offset: Optional[AccessorValue] = None,
        # Size settings
        size_units: Optional[str] = None,
        size_scale: Optional[float] = None,
        size_min_pixels: Optional[float] = None,
        size_max_pixels: Optional[float] = None,
        # Font settings
        font_family: Optional[str] = None,
        font_weight: Optional[Union[str, int]] = None,
        character_set: Optional[Union[str, List[str]]] = None,
        line_height: Optional[float] = None,
        max_width: Optional[float] = None,
        word_break: Optional[str] = None,  # 'break-word' | 'break-all'
        # Background
        background: Optional[bool] = None,
        background_color: Optional[ColorValue] = None,
        get_background_color: Optional[AccessorValue] = None,
        background_padding: Optional[Union[float, List[float]]] = None,
        # Rendering
        billboard: Optional[bool] = None,
        outline_width: Optional[float] = None,
        outline_color: Optional[ColorValue] = None,
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
        self._set_prop('get_position', get_position)
        self._set_prop('get_text', get_text)
        # Style
        self._set_prop('get_size', get_size)
        self._set_prop('get_color', get_color)
        self._set_prop('get_angle', get_angle)
        self._set_prop('get_text_anchor', get_text_anchor)
        self._set_prop('get_alignment_baseline', get_alignment_baseline)
        self._set_prop('get_pixel_offset', get_pixel_offset)
        # Size
        self._set_prop('size_units', size_units)
        self._set_prop('size_scale', size_scale)
        self._set_prop('size_min_pixels', size_min_pixels)
        self._set_prop('size_max_pixels', size_max_pixels)
        # Font
        self._set_prop('font_family', font_family)
        self._set_prop('font_weight', font_weight)
        self._set_prop('character_set', character_set)
        self._set_prop('line_height', line_height)
        self._set_prop('max_width', max_width)
        self._set_prop('word_break', word_break)
        # Background
        self._set_prop('background', background)
        self._set_prop('background_color', background_color)
        self._set_prop('get_background_color', get_background_color)
        self._set_prop('background_padding', background_padding)
        # Rendering
        self._set_prop('billboard', billboard)
        self._set_prop('outline_width', outline_width)
        self._set_prop('outline_color', outline_color)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class PolygonLayer(BaseLayer):
    """Render filled and/or stroked polygons.

    Example:
        >>> PolygonLayer(
        ...     id='polygons',
        ...     data=regions,
        ...     get_polygon='@@=coordinates',
        ...     get_fill_color=[255, 140, 0, 200],
        ...     get_line_color=[0, 0, 0],
        ...     get_line_width=2,
        ...     pickable=True
        ... )
    """
    _layer_type = 'PolygonLayer'
    _color_props = ('get_fill_color', 'get_line_color')
    _accessor_props = ('get_polygon', 'get_fill_color', 'get_line_color', 'get_line_width', 'get_elevation')

    def __init__(
        self, id: str, data: Any, *,
        # Position accessor
        get_polygon: Optional[AccessorValue] = None,
        # Rendering
        filled: Optional[bool] = None,
        stroked: Optional[bool] = None,
        extruded: Optional[bool] = None,
        wireframe: Optional[bool] = None,
        # Style accessors
        get_fill_color: Optional[AccessorValue] = None,
        get_line_color: Optional[AccessorValue] = None,
        get_line_width: Optional[AccessorValue] = None,
        get_elevation: Optional[AccessorValue] = None,
        # Width settings
        line_width_units: Optional[str] = None,
        line_width_scale: Optional[float] = None,
        line_width_min_pixels: Optional[float] = None,
        line_width_max_pixels: Optional[float] = None,
        # Elevation
        elevation_scale: Optional[float] = None,
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
        self._set_prop('get_polygon', get_polygon)
        # Rendering
        self._set_prop('filled', filled)
        self._set_prop('stroked', stroked)
        self._set_prop('extruded', extruded)
        self._set_prop('wireframe', wireframe)
        # Style
        self._set_prop('get_fill_color', get_fill_color)
        self._set_prop('get_line_color', get_line_color)
        self._set_prop('get_line_width', get_line_width)
        self._set_prop('get_elevation', get_elevation)
        # Width
        self._set_prop('line_width_units', line_width_units)
        self._set_prop('line_width_scale', line_width_scale)
        self._set_prop('line_width_min_pixels', line_width_min_pixels)
        self._set_prop('line_width_max_pixels', line_width_max_pixels)
        # Elevation
        self._set_prop('elevation_scale', elevation_scale)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)
