"""MapLibre layer classes for deckgl-dash.

These are MapLibre GL JS style layers, NOT deck.gl layers.
Use these for styling vector tile data rendered by MapLibre.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union

# Type alias for MapLibre expressions
Expression = List[Any]
# Type alias for paint/layout property values (static or expression)
PropertyValue = Union[str, int, float, bool, List[Any], Expression]


class BaseMapLibreLayer:
    """Base class for MapLibre style layers."""

    _layer_type: str = ''

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        min_zoom: Optional[float] = None,
        max_zoom: Optional[float] = None,
        filter: Optional[Expression] = None,
        layout: Optional[Dict[str, PropertyValue]] = None,
        paint: Optional[Dict[str, PropertyValue]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize MapLibre layer.

        Args:
            id: Unique layer ID.
            source: Source ID to use for this layer.
            source_layer: Source layer name (required for vector tile sources).
            min_zoom: Minimum zoom level for layer visibility.
            max_zoom: Maximum zoom level for layer visibility.
            filter: MapLibre filter expression.
            layout: Layout properties dict.
            paint: Paint properties dict.
            metadata: Arbitrary metadata dict.
        """
        self.id = id
        self.source = source
        self.source_layer = source_layer
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.filter = filter
        self.layout = layout or {}
        self.paint = paint or {}
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MapLibre layer spec dict."""
        result: Dict[str, Any] = {'id': self.id, 'type': self._layer_type, 'source': self.source}
        if self.source_layer:
            result['source-layer'] = self.source_layer
        if self.min_zoom is not None:
            result['minzoom'] = self.min_zoom
        if self.max_zoom is not None:
            result['maxzoom'] = self.max_zoom
        if self.filter:
            result['filter'] = self.filter
        if self.layout:
            result['layout'] = self.layout
        if self.paint:
            result['paint'] = self.paint
        if self.metadata:
            result['metadata'] = self.metadata
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, source={self.source!r})"


class FillLayer(BaseMapLibreLayer):
    """MapLibre fill layer for rendering filled polygons.

    Example:
        >>> layer = FillLayer(
        ...     id='buildings',
        ...     source='vector-tiles',
        ...     source_layer='building',
        ...     paint={
        ...         'fill-color': '#ff0000',
        ...         'fill-opacity': 0.5,
        ...     },
        ... )
    """

    _layer_type = 'fill'

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        # Common paint properties
        fill_color: Optional[PropertyValue] = None,
        fill_opacity: Optional[PropertyValue] = None,
        fill_outline_color: Optional[PropertyValue] = None,
        fill_pattern: Optional[PropertyValue] = None,
        fill_antialias: Optional[bool] = None,
        fill_translate: Optional[List[float]] = None,
        fill_translate_anchor: Optional[str] = None,
        # Common layout properties
        visibility: Optional[str] = None,
        fill_sort_key: Optional[PropertyValue] = None,
        **kwargs
    ):
        super().__init__(id, source, source_layer, **kwargs)
        # Build paint dict from convenience args
        if fill_color is not None:
            self.paint['fill-color'] = fill_color
        if fill_opacity is not None:
            self.paint['fill-opacity'] = fill_opacity
        if fill_outline_color is not None:
            self.paint['fill-outline-color'] = fill_outline_color
        if fill_pattern is not None:
            self.paint['fill-pattern'] = fill_pattern
        if fill_antialias is not None:
            self.paint['fill-antialias'] = fill_antialias
        if fill_translate is not None:
            self.paint['fill-translate'] = fill_translate
        if fill_translate_anchor is not None:
            self.paint['fill-translate-anchor'] = fill_translate_anchor
        # Layout
        if visibility is not None:
            self.layout['visibility'] = visibility
        if fill_sort_key is not None:
            self.layout['fill-sort-key'] = fill_sort_key


class LineLayer(BaseMapLibreLayer):
    """MapLibre line layer for rendering lines and polygon outlines.

    Example:
        >>> layer = LineLayer(
        ...     id='roads',
        ...     source='vector-tiles',
        ...     source_layer='road',
        ...     paint={
        ...         'line-color': '#000000',
        ...         'line-width': 2,
        ...     },
        ... )
    """

    _layer_type = 'line'

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        # Common paint properties
        line_color: Optional[PropertyValue] = None,
        line_width: Optional[PropertyValue] = None,
        line_opacity: Optional[PropertyValue] = None,
        line_blur: Optional[PropertyValue] = None,
        line_dasharray: Optional[List[float]] = None,
        line_gap_width: Optional[PropertyValue] = None,
        line_offset: Optional[PropertyValue] = None,
        line_pattern: Optional[PropertyValue] = None,
        line_translate: Optional[List[float]] = None,
        line_translate_anchor: Optional[str] = None,
        line_gradient: Optional[Expression] = None,
        # Common layout properties
        visibility: Optional[str] = None,
        line_cap: Optional[str] = None,
        line_join: Optional[str] = None,
        line_miter_limit: Optional[float] = None,
        line_round_limit: Optional[float] = None,
        line_sort_key: Optional[PropertyValue] = None,
        **kwargs
    ):
        super().__init__(id, source, source_layer, **kwargs)
        # Paint
        if line_color is not None:
            self.paint['line-color'] = line_color
        if line_width is not None:
            self.paint['line-width'] = line_width
        if line_opacity is not None:
            self.paint['line-opacity'] = line_opacity
        if line_blur is not None:
            self.paint['line-blur'] = line_blur
        if line_dasharray is not None:
            self.paint['line-dasharray'] = line_dasharray
        if line_gap_width is not None:
            self.paint['line-gap-width'] = line_gap_width
        if line_offset is not None:
            self.paint['line-offset'] = line_offset
        if line_pattern is not None:
            self.paint['line-pattern'] = line_pattern
        if line_translate is not None:
            self.paint['line-translate'] = line_translate
        if line_translate_anchor is not None:
            self.paint['line-translate-anchor'] = line_translate_anchor
        if line_gradient is not None:
            self.paint['line-gradient'] = line_gradient
        # Layout
        if visibility is not None:
            self.layout['visibility'] = visibility
        if line_cap is not None:
            self.layout['line-cap'] = line_cap
        if line_join is not None:
            self.layout['line-join'] = line_join
        if line_miter_limit is not None:
            self.layout['line-miter-limit'] = line_miter_limit
        if line_round_limit is not None:
            self.layout['line-round-limit'] = line_round_limit
        if line_sort_key is not None:
            self.layout['line-sort-key'] = line_sort_key


class RasterLayer(BaseMapLibreLayer):
    """MapLibre raster layer for rendering raster tile sources.

    Example:
        >>> layer = RasterLayer(
        ...     id='satellite',
        ...     source='satellite-tiles',
        ...     paint={'raster-opacity': 0.8},
        ... )
    """

    _layer_type = 'raster'

    def __init__(
        self,
        id: str,
        source: str,
        # Common paint properties
        raster_opacity: Optional[float] = None,
        raster_hue_rotate: Optional[float] = None,
        raster_brightness_min: Optional[float] = None,
        raster_brightness_max: Optional[float] = None,
        raster_saturation: Optional[float] = None,
        raster_contrast: Optional[float] = None,
        raster_resampling: Optional[str] = None,
        raster_fade_duration: Optional[float] = None,
        # Common layout properties
        visibility: Optional[str] = None,
        **kwargs
    ):
        # Raster layers don't use source_layer
        super().__init__(id, source, source_layer=None, **kwargs)
        # Paint
        if raster_opacity is not None:
            self.paint['raster-opacity'] = raster_opacity
        if raster_hue_rotate is not None:
            self.paint['raster-hue-rotate'] = raster_hue_rotate
        if raster_brightness_min is not None:
            self.paint['raster-brightness-min'] = raster_brightness_min
        if raster_brightness_max is not None:
            self.paint['raster-brightness-max'] = raster_brightness_max
        if raster_saturation is not None:
            self.paint['raster-saturation'] = raster_saturation
        if raster_contrast is not None:
            self.paint['raster-contrast'] = raster_contrast
        if raster_resampling is not None:
            self.paint['raster-resampling'] = raster_resampling
        if raster_fade_duration is not None:
            self.paint['raster-fade-duration'] = raster_fade_duration
        # Layout
        if visibility is not None:
            self.layout['visibility'] = visibility


class CircleLayer(BaseMapLibreLayer):
    """MapLibre circle layer for rendering points as circles.

    Example:
        >>> layer = CircleLayer(
        ...     id='points',
        ...     source='geojson-points',
        ...     paint={
        ...         'circle-radius': 6,
        ...         'circle-color': '#007cbf',
        ...     },
        ... )
    """

    _layer_type = 'circle'

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        # Common paint properties
        circle_radius: Optional[PropertyValue] = None,
        circle_color: Optional[PropertyValue] = None,
        circle_blur: Optional[PropertyValue] = None,
        circle_opacity: Optional[PropertyValue] = None,
        circle_stroke_width: Optional[PropertyValue] = None,
        circle_stroke_color: Optional[PropertyValue] = None,
        circle_stroke_opacity: Optional[PropertyValue] = None,
        circle_translate: Optional[List[float]] = None,
        circle_translate_anchor: Optional[str] = None,
        circle_pitch_scale: Optional[str] = None,
        circle_pitch_alignment: Optional[str] = None,
        # Common layout properties
        visibility: Optional[str] = None,
        circle_sort_key: Optional[PropertyValue] = None,
        **kwargs
    ):
        super().__init__(id, source, source_layer, **kwargs)
        # Paint
        if circle_radius is not None:
            self.paint['circle-radius'] = circle_radius
        if circle_color is not None:
            self.paint['circle-color'] = circle_color
        if circle_blur is not None:
            self.paint['circle-blur'] = circle_blur
        if circle_opacity is not None:
            self.paint['circle-opacity'] = circle_opacity
        if circle_stroke_width is not None:
            self.paint['circle-stroke-width'] = circle_stroke_width
        if circle_stroke_color is not None:
            self.paint['circle-stroke-color'] = circle_stroke_color
        if circle_stroke_opacity is not None:
            self.paint['circle-stroke-opacity'] = circle_stroke_opacity
        if circle_translate is not None:
            self.paint['circle-translate'] = circle_translate
        if circle_translate_anchor is not None:
            self.paint['circle-translate-anchor'] = circle_translate_anchor
        if circle_pitch_scale is not None:
            self.paint['circle-pitch-scale'] = circle_pitch_scale
        if circle_pitch_alignment is not None:
            self.paint['circle-pitch-alignment'] = circle_pitch_alignment
        # Layout
        if visibility is not None:
            self.layout['visibility'] = visibility
        if circle_sort_key is not None:
            self.layout['circle-sort-key'] = circle_sort_key


class SymbolLayer(BaseMapLibreLayer):
    """MapLibre symbol layer for rendering text labels and icons.

    Example:
        >>> layer = SymbolLayer(
        ...     id='labels',
        ...     source='places',
        ...     layout={
        ...         'text-field': ['get', 'name'],
        ...         'text-size': 12,
        ...     },
        ...     paint={
        ...         'text-color': '#000000',
        ...     },
        ... )
    """

    _layer_type = 'symbol'

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        # Common layout properties (symbols use layout heavily)
        text_field: Optional[PropertyValue] = None,
        text_size: Optional[PropertyValue] = None,
        text_font: Optional[List[str]] = None,
        text_anchor: Optional[str] = None,
        text_offset: Optional[List[float]] = None,
        text_max_width: Optional[PropertyValue] = None,
        text_justify: Optional[str] = None,
        text_rotation_alignment: Optional[str] = None,
        text_pitch_alignment: Optional[str] = None,
        text_transform: Optional[str] = None,
        text_letter_spacing: Optional[PropertyValue] = None,
        text_line_height: Optional[PropertyValue] = None,
        icon_image: Optional[PropertyValue] = None,
        icon_size: Optional[PropertyValue] = None,
        icon_anchor: Optional[str] = None,
        icon_offset: Optional[List[float]] = None,
        icon_rotation_alignment: Optional[str] = None,
        icon_pitch_alignment: Optional[str] = None,
        symbol_placement: Optional[str] = None,
        symbol_spacing: Optional[float] = None,
        symbol_sort_key: Optional[PropertyValue] = None,
        visibility: Optional[str] = None,
        # Common paint properties
        text_color: Optional[PropertyValue] = None,
        text_opacity: Optional[PropertyValue] = None,
        text_halo_color: Optional[PropertyValue] = None,
        text_halo_width: Optional[PropertyValue] = None,
        text_halo_blur: Optional[PropertyValue] = None,
        icon_color: Optional[PropertyValue] = None,
        icon_opacity: Optional[PropertyValue] = None,
        icon_halo_color: Optional[PropertyValue] = None,
        icon_halo_width: Optional[PropertyValue] = None,
        icon_halo_blur: Optional[PropertyValue] = None,
        **kwargs
    ):
        super().__init__(id, source, source_layer, **kwargs)
        # Layout (symbol layers use layout for most styling)
        if text_field is not None:
            self.layout['text-field'] = text_field
        if text_size is not None:
            self.layout['text-size'] = text_size
        if text_font is not None:
            self.layout['text-font'] = text_font
        if text_anchor is not None:
            self.layout['text-anchor'] = text_anchor
        if text_offset is not None:
            self.layout['text-offset'] = text_offset
        if text_max_width is not None:
            self.layout['text-max-width'] = text_max_width
        if text_justify is not None:
            self.layout['text-justify'] = text_justify
        if text_rotation_alignment is not None:
            self.layout['text-rotation-alignment'] = text_rotation_alignment
        if text_pitch_alignment is not None:
            self.layout['text-pitch-alignment'] = text_pitch_alignment
        if text_transform is not None:
            self.layout['text-transform'] = text_transform
        if text_letter_spacing is not None:
            self.layout['text-letter-spacing'] = text_letter_spacing
        if text_line_height is not None:
            self.layout['text-line-height'] = text_line_height
        if icon_image is not None:
            self.layout['icon-image'] = icon_image
        if icon_size is not None:
            self.layout['icon-size'] = icon_size
        if icon_anchor is not None:
            self.layout['icon-anchor'] = icon_anchor
        if icon_offset is not None:
            self.layout['icon-offset'] = icon_offset
        if icon_rotation_alignment is not None:
            self.layout['icon-rotation-alignment'] = icon_rotation_alignment
        if icon_pitch_alignment is not None:
            self.layout['icon-pitch-alignment'] = icon_pitch_alignment
        if symbol_placement is not None:
            self.layout['symbol-placement'] = symbol_placement
        if symbol_spacing is not None:
            self.layout['symbol-spacing'] = symbol_spacing
        if symbol_sort_key is not None:
            self.layout['symbol-sort-key'] = symbol_sort_key
        if visibility is not None:
            self.layout['visibility'] = visibility
        # Paint
        if text_color is not None:
            self.paint['text-color'] = text_color
        if text_opacity is not None:
            self.paint['text-opacity'] = text_opacity
        if text_halo_color is not None:
            self.paint['text-halo-color'] = text_halo_color
        if text_halo_width is not None:
            self.paint['text-halo-width'] = text_halo_width
        if text_halo_blur is not None:
            self.paint['text-halo-blur'] = text_halo_blur
        if icon_color is not None:
            self.paint['icon-color'] = icon_color
        if icon_opacity is not None:
            self.paint['icon-opacity'] = icon_opacity
        if icon_halo_color is not None:
            self.paint['icon-halo-color'] = icon_halo_color
        if icon_halo_width is not None:
            self.paint['icon-halo-width'] = icon_halo_width
        if icon_halo_blur is not None:
            self.paint['icon-halo-blur'] = icon_halo_blur


class FillExtrusionLayer(BaseMapLibreLayer):
    """MapLibre fill-extrusion layer for rendering 3D extruded polygons.

    Example:
        >>> layer = FillExtrusionLayer(
        ...     id='buildings-3d',
        ...     source='vector-tiles',
        ...     source_layer='building',
        ...     paint={
        ...         'fill-extrusion-color': '#aaa',
        ...         'fill-extrusion-height': ['get', 'height'],
        ...         'fill-extrusion-base': ['get', 'min_height'],
        ...         'fill-extrusion-opacity': 0.6,
        ...     },
        ... )
    """

    _layer_type = 'fill-extrusion'

    def __init__(
        self,
        id: str,
        source: str,
        source_layer: Optional[str] = None,
        # Common paint properties
        fill_extrusion_color: Optional[PropertyValue] = None,
        fill_extrusion_opacity: Optional[float] = None,
        fill_extrusion_height: Optional[PropertyValue] = None,
        fill_extrusion_base: Optional[PropertyValue] = None,
        fill_extrusion_pattern: Optional[PropertyValue] = None,
        fill_extrusion_translate: Optional[List[float]] = None,
        fill_extrusion_translate_anchor: Optional[str] = None,
        fill_extrusion_vertical_gradient: Optional[bool] = None,
        # Common layout properties
        visibility: Optional[str] = None,
        fill_extrusion_edge_radius: Optional[float] = None,
        **kwargs
    ):
        super().__init__(id, source, source_layer, **kwargs)
        # Paint
        if fill_extrusion_color is not None:
            self.paint['fill-extrusion-color'] = fill_extrusion_color
        if fill_extrusion_opacity is not None:
            self.paint['fill-extrusion-opacity'] = fill_extrusion_opacity
        if fill_extrusion_height is not None:
            self.paint['fill-extrusion-height'] = fill_extrusion_height
        if fill_extrusion_base is not None:
            self.paint['fill-extrusion-base'] = fill_extrusion_base
        if fill_extrusion_pattern is not None:
            self.paint['fill-extrusion-pattern'] = fill_extrusion_pattern
        if fill_extrusion_translate is not None:
            self.paint['fill-extrusion-translate'] = fill_extrusion_translate
        if fill_extrusion_translate_anchor is not None:
            self.paint['fill-extrusion-translate-anchor'] = fill_extrusion_translate_anchor
        if fill_extrusion_vertical_gradient is not None:
            self.paint['fill-extrusion-vertical-gradient'] = fill_extrusion_vertical_gradient
        # Layout
        if visibility is not None:
            self.layout['visibility'] = visibility
        if fill_extrusion_edge_radius is not None:
            self.layout['fill-extrusion-edge-radius'] = fill_extrusion_edge_radius
