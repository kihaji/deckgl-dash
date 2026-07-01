"""Drawing configuration for the DeckGL component."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .layers.base import ColorValue, normalize_color

DRAWING_MODES = {'draw_line', 'draw_polygon', 'draw_circle', 'draw_rectangle', 'draw_square', 'draw_point', 'view', 'modify', 'translate', 'delete'}

EMPTY_FEATURE_COLLECTION: Dict[str, Any] = {"type": "FeatureCollection", "features": []}


class DrawingStyle:
    """Style configuration for drawn features.

    Args:
        fill_color: Fill color for completed features (hex, RGB tuple, or RGBA list).
        line_color: Stroke color for completed features.
        line_width: Stroke width in pixels.
        tentative_fill_color: Fill color for features while being drawn.
        tentative_line_color: Stroke color for features while being drawn.
        edit_handle_point_color: Color of vertex edit handles in modify mode.
        point_radius: Radius of drawn points in pixels. Defaults to 5.
        show_measurements: Whether to show distance/area tooltips while drawing lines and circles. Defaults to True.
    """

    def __init__(
        self, *, fill_color: Optional[ColorValue] = None, line_color: Optional[ColorValue] = None,
        line_width: Optional[float] = None, tentative_fill_color: Optional[ColorValue] = None,
        tentative_line_color: Optional[ColorValue] = None, edit_handle_point_color: Optional[ColorValue] = None,
        point_radius: Optional[float] = None, show_measurements: Optional[bool] = None,
    ):
        self._props: Dict[str, Any] = {}
        if fill_color is not None:
            self._props['fillColor'] = normalize_color(fill_color)
        if line_color is not None:
            self._props['lineColor'] = normalize_color(line_color)
        if line_width is not None:
            self._props['lineWidth'] = line_width
        if tentative_fill_color is not None:
            self._props['tentativeFillColor'] = normalize_color(tentative_fill_color)
        if tentative_line_color is not None:
            self._props['tentativeLineColor'] = normalize_color(tentative_line_color)
        if edit_handle_point_color is not None:
            self._props['editHandlePointColor'] = normalize_color(edit_handle_point_color)
        if point_radius is not None:
            self._props['pointRadius'] = point_radius
        if show_measurements is not None:
            self._props['showMeasurements'] = show_measurements

    def to_dict(self) -> Dict[str, Any]:
        return self._props


class DrawingConfig:
    """Configuration for the drawing/editing system.

    Args:
        mode: Drawing mode string. One of: 'draw_line', 'draw_polygon', 'draw_circle',
            'draw_rectangle', 'draw_square', 'draw_point', 'view', 'modify', 'translate', 'delete'.
            In 'delete' mode, each click on a feature deletes it.
        selected_feature_indexes: Indexes of features selected for editing (used with 'modify'/'translate' modes).
        style: Optional style overrides for the drawing layer.
        delete_selected: Set to True to delete the currently selected feature(s). Automatically resets to False.

    Example:
        >>> config = DrawingConfig(
        ...     mode = 'draw_polygon',
        ...     style = DrawingStyle(fill_color = [255, 140, 0, 100], line_color = '#000000', line_width = 2),
        ... )
    """

    def __init__(
        self, mode: str = 'view', *, selected_feature_indexes: Optional[List[int]] = None,
        style: Optional[DrawingStyle] = None, delete_selected: bool = False,
    ):
        if mode not in DRAWING_MODES:
            raise ValueError(f"Invalid drawing mode '{mode}'. Must be one of: {sorted(DRAWING_MODES)}")
        self.mode = mode
        self.selected_feature_indexes = selected_feature_indexes or []
        self.style = style
        self.delete_selected = delete_selected

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {'mode': self.mode}
        if self.selected_feature_indexes:
            result['selectedFeatureIndexes'] = self.selected_feature_indexes
        if self.style:
            result['style'] = self.style.to_dict()
        if self.delete_selected:
            result['deleteSelected'] = True
        return result
