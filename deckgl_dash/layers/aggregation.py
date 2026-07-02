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
        super().__init__(id, data = data, get_position = get_position, get_weight = get_weight, radius_pixels = radius_pixels,
                         intensity = intensity, threshold = threshold, color_range = color_range, color_domain = color_domain,
                         aggregation = aggregation, weights_texture_size = weights_texture_size, debounce_timeout = debounce_timeout,
                         pickable = pickable, opacity = opacity, visible = visible, **kwargs)


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
        super().__init__(id, data = data, get_position = get_position, radius = radius, coverage = coverage, extruded = extruded,
                         elevation_scale = elevation_scale, elevation_range = elevation_range, color_range = color_range,
                         color_domain = color_domain, color_scale_type = color_scale_type, get_color_weight = get_color_weight,
                         color_aggregation = color_aggregation, get_elevation_weight = get_elevation_weight,
                         elevation_aggregation = elevation_aggregation, upper_percentile = upper_percentile, lower_percentile = lower_percentile,
                         elevation_upper_percentile = elevation_upper_percentile, elevation_lower_percentile = elevation_lower_percentile,
                         material = material, pickable = pickable, auto_highlight = auto_highlight, highlight_color = highlight_color,
                         opacity = opacity, visible = visible, **kwargs)


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
        super().__init__(id, data = data, get_position = get_position, cell_size = cell_size, coverage = coverage, extruded = extruded,
                         elevation_scale = elevation_scale, elevation_range = elevation_range, color_range = color_range,
                         color_domain = color_domain, color_scale_type = color_scale_type, get_color_weight = get_color_weight,
                         color_aggregation = color_aggregation, get_elevation_weight = get_elevation_weight,
                         elevation_aggregation = elevation_aggregation, upper_percentile = upper_percentile, lower_percentile = lower_percentile,
                         elevation_upper_percentile = elevation_upper_percentile, elevation_lower_percentile = elevation_lower_percentile,
                         material = material, pickable = pickable, auto_highlight = auto_highlight, highlight_color = highlight_color,
                         opacity = opacity, visible = visible, **kwargs)
