"""Aggregation layer helpers for dash-deckgl (from @deck.gl/aggregation-layers)."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from .base import BaseLayer, AccessorValue, ColorValue


class HeatmapLayer(BaseLayer):
    """Render a heatmap based on point density.

    Example:
        >>> HeatmapLayer(
        ...     id='heatmap',
        ...     data=points,
        ...     get_position='@@=coordinates',
        ...     get_weight=1,
        ...     radius_pixels=30,
        ...     intensity=1,
        ...     threshold=0.03
        ... )
    """
    _layer_type = 'HeatmapLayer'
    _color_props = ()
    _accessor_props = ('get_position', 'get_weight')

    def __init__(
        self, id: str, data: Any, *,
        # Position & weight
        get_position: Optional[AccessorValue] = None,
        get_weight: Optional[AccessorValue] = None,
        # Heatmap settings
        radius_pixels: Optional[float] = None,
        intensity: Optional[float] = None,
        threshold: Optional[float] = None,
        # Color scale
        color_range: Optional[Sequence[ColorValue]] = None,
        color_domain: Optional[List[float]] = None,
        # Aggregation
        aggregation: Optional[str] = None,  # 'SUM' | 'MEAN'
        weights_texture_size: Optional[int] = None,
        debounce_timeout: Optional[int] = None,
        # Interaction
        pickable: Optional[bool] = None,
        # Other
        opacity: Optional[float] = None,
        visible: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(id)
        self._set_prop('data', data)
        self._set_prop('get_position', get_position)
        self._set_prop('get_weight', get_weight)
        # Heatmap
        self._set_prop('radius_pixels', radius_pixels)
        self._set_prop('intensity', intensity)
        self._set_prop('threshold', threshold)
        # Color scale
        self._set_prop('color_range', color_range)
        self._set_prop('color_domain', color_domain)
        # Aggregation
        self._set_prop('aggregation', aggregation)
        self._set_prop('weights_texture_size', weights_texture_size)
        self._set_prop('debounce_timeout', debounce_timeout)
        # Interaction
        self._set_prop('pickable', pickable)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class HexagonLayer(BaseLayer):
    """Render data aggregated into hexagonal bins.

    Example:
        >>> HexagonLayer(
        ...     id='hexagons',
        ...     data=points,
        ...     get_position='@@=coordinates',
        ...     radius=1000,
        ...     elevation_scale=100,
        ...     extruded=True,
        ...     pickable=True
        ... )
    """
    _layer_type = 'HexagonLayer'
    _color_props = ()
    _accessor_props = ('get_position', 'get_color_weight', 'get_elevation_weight')

    def __init__(
        self, id: str, data: Any, *,
        # Position
        get_position: Optional[AccessorValue] = None,
        # Hexagon settings
        radius: Optional[float] = None,  # meters
        coverage: Optional[float] = None,  # 0-1
        # 3D settings
        extruded: Optional[bool] = None,
        elevation_scale: Optional[float] = None,
        elevation_range: Optional[List[float]] = None,
        # Color settings
        color_range: Optional[Sequence[ColorValue]] = None,
        color_domain: Optional[List[float]] = None,
        color_scale_type: Optional[str] = None,  # 'quantize' | 'quantile' | 'ordinal'
        # Weight accessors
        get_color_weight: Optional[AccessorValue] = None,
        color_aggregation: Optional[str] = None,  # 'SUM' | 'MEAN' | 'MIN' | 'MAX'
        get_elevation_weight: Optional[AccessorValue] = None,
        elevation_aggregation: Optional[str] = None,
        # Lower/upper percentile for filtering
        upper_percentile: Optional[float] = None,
        lower_percentile: Optional[float] = None,
        elevation_upper_percentile: Optional[float] = None,
        elevation_lower_percentile: Optional[float] = None,
        # Rendering
        material: Optional[Union[bool, Dict[str, Any]]] = None,
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
        # Hexagon
        self._set_prop('radius', radius)
        self._set_prop('coverage', coverage)
        # 3D
        self._set_prop('extruded', extruded)
        self._set_prop('elevation_scale', elevation_scale)
        self._set_prop('elevation_range', elevation_range)
        # Color
        self._set_prop('color_range', color_range)
        self._set_prop('color_domain', color_domain)
        self._set_prop('color_scale_type', color_scale_type)
        # Weight
        self._set_prop('get_color_weight', get_color_weight)
        self._set_prop('color_aggregation', color_aggregation)
        self._set_prop('get_elevation_weight', get_elevation_weight)
        self._set_prop('elevation_aggregation', elevation_aggregation)
        # Percentile
        self._set_prop('upper_percentile', upper_percentile)
        self._set_prop('lower_percentile', lower_percentile)
        self._set_prop('elevation_upper_percentile', elevation_upper_percentile)
        self._set_prop('elevation_lower_percentile', elevation_lower_percentile)
        # Rendering
        self._set_prop('material', material)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)


class GridLayer(BaseLayer):
    """Render data aggregated into a square grid.

    Example:
        >>> GridLayer(
        ...     id='grid',
        ...     data=points,
        ...     get_position='@@=coordinates',
        ...     cell_size=200,
        ...     elevation_scale=50,
        ...     extruded=True,
        ...     pickable=True
        ... )
    """
    _layer_type = 'GridLayer'
    _color_props = ()
    _accessor_props = ('get_position', 'get_color_weight', 'get_elevation_weight')

    def __init__(
        self, id: str, data: Any, *,
        # Position
        get_position: Optional[AccessorValue] = None,
        # Grid settings
        cell_size: Optional[float] = None,  # meters
        coverage: Optional[float] = None,  # 0-1
        # 3D settings
        extruded: Optional[bool] = None,
        elevation_scale: Optional[float] = None,
        elevation_range: Optional[List[float]] = None,
        # Color settings
        color_range: Optional[Sequence[ColorValue]] = None,
        color_domain: Optional[List[float]] = None,
        color_scale_type: Optional[str] = None,
        # Weight accessors
        get_color_weight: Optional[AccessorValue] = None,
        color_aggregation: Optional[str] = None,
        get_elevation_weight: Optional[AccessorValue] = None,
        elevation_aggregation: Optional[str] = None,
        # Lower/upper percentile
        upper_percentile: Optional[float] = None,
        lower_percentile: Optional[float] = None,
        elevation_upper_percentile: Optional[float] = None,
        elevation_lower_percentile: Optional[float] = None,
        # Rendering
        material: Optional[Union[bool, Dict[str, Any]]] = None,
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
        # Grid
        self._set_prop('cell_size', cell_size)
        self._set_prop('coverage', coverage)
        # 3D
        self._set_prop('extruded', extruded)
        self._set_prop('elevation_scale', elevation_scale)
        self._set_prop('elevation_range', elevation_range)
        # Color
        self._set_prop('color_range', color_range)
        self._set_prop('color_domain', color_domain)
        self._set_prop('color_scale_type', color_scale_type)
        # Weight
        self._set_prop('get_color_weight', get_color_weight)
        self._set_prop('color_aggregation', color_aggregation)
        self._set_prop('get_elevation_weight', get_elevation_weight)
        self._set_prop('elevation_aggregation', elevation_aggregation)
        # Percentile
        self._set_prop('upper_percentile', upper_percentile)
        self._set_prop('lower_percentile', lower_percentile)
        self._set_prop('elevation_upper_percentile', elevation_upper_percentile)
        self._set_prop('elevation_lower_percentile', elevation_lower_percentile)
        # Rendering
        self._set_prop('material', material)
        # Interaction
        self._set_prop('pickable', pickable)
        self._set_prop('auto_highlight', auto_highlight)
        self._set_prop('highlight_color', highlight_color)
        # Other
        self._set_prop('opacity', opacity)
        self._set_prop('visible', visible)
        for key, value in kwargs.items():
            self._set_prop(key, value)
