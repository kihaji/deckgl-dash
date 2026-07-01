"""Tests for drawing configuration helpers."""
import pytest
from deckgl_dash.drawing import DrawingConfig, DrawingStyle, DRAWING_MODES, EMPTY_FEATURE_COLLECTION


class TestDrawingStyle:
    def test_empty_style(self):
        style = DrawingStyle()
        assert style.to_dict() == {}

    def test_fill_color_hex(self):
        style = DrawingStyle(fill_color = '#FF8C00')
        assert style.to_dict() == {'fillColor': [255, 140, 0]}

    def test_fill_color_rgba_list(self):
        style = DrawingStyle(fill_color = [255, 140, 0, 100])
        assert style.to_dict() == {'fillColor': [255, 140, 0, 100]}

    def test_line_color_tuple(self):
        style = DrawingStyle(line_color = (0, 0, 0))
        assert style.to_dict() == {'lineColor': [0, 0, 0]}

    def test_line_width(self):
        style = DrawingStyle(line_width = 3.5)
        assert style.to_dict() == {'lineWidth': 3.5}

    def test_tentative_colors(self):
        style = DrawingStyle(tentative_fill_color = '#FF000080', tentative_line_color = '#00FF00')
        result = style.to_dict()
        assert result['tentativeFillColor'] == [255, 0, 0, 128]
        assert result['tentativeLineColor'] == [0, 255, 0]

    def test_edit_handle_color(self):
        style = DrawingStyle(edit_handle_point_color = [255, 0, 0, 255])
        assert style.to_dict() == {'editHandlePointColor': [255, 0, 0, 255]}

    def test_show_measurements_false(self):
        style = DrawingStyle(show_measurements = False)
        assert style.to_dict() == {'showMeasurements': False}

    def test_show_measurements_true(self):
        style = DrawingStyle(show_measurements = True)
        assert style.to_dict() == {'showMeasurements': True}

    def test_point_radius(self):
        style = DrawingStyle(point_radius = 10)
        assert style.to_dict() == {'pointRadius': 10}

    def test_point_radius_omitted_by_default(self):
        style = DrawingStyle(fill_color = '#FF0000')
        assert 'pointRadius' not in style.to_dict()

    def test_show_measurements_omitted_by_default(self):
        style = DrawingStyle(fill_color = '#FF0000')
        assert 'showMeasurements' not in style.to_dict()

    def test_all_properties(self):
        style = DrawingStyle(
            fill_color = [255, 140, 0, 100], line_color = '#333333', line_width = 2,
            tentative_fill_color = [255, 140, 0, 50], tentative_line_color = '#FF8C00',
            edit_handle_point_color = [255, 0, 0, 255], show_measurements = False,
        )
        result = style.to_dict()
        assert len(result) == 7
        assert result['lineWidth'] == 2
        assert result['showMeasurements'] is False


class TestDrawingConfig:
    def test_default_view_mode(self):
        config = DrawingConfig()
        assert config.mode == 'view'
        assert config.to_dict() == {'mode': 'view'}

    def test_draw_polygon_mode(self):
        config = DrawingConfig(mode = 'draw_polygon')
        assert config.to_dict() == {'mode': 'draw_polygon'}

    def test_all_valid_modes(self):
        for mode in DRAWING_MODES:
            config = DrawingConfig(mode = mode)
            assert config.mode == mode

    def test_delete_mode(self):
        config = DrawingConfig(mode = 'delete')
        assert config.to_dict() == {'mode': 'delete'}

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match = "Invalid drawing mode 'invalid'"):
            DrawingConfig(mode = 'invalid')

    def test_selected_feature_indexes(self):
        config = DrawingConfig(mode = 'modify', selected_feature_indexes = [0, 2])
        result = config.to_dict()
        assert result['selectedFeatureIndexes'] == [0, 2]

    def test_empty_selected_indexes_omitted(self):
        config = DrawingConfig(mode = 'view', selected_feature_indexes = [])
        result = config.to_dict()
        assert 'selectedFeatureIndexes' not in result

    def test_with_style(self):
        style = DrawingStyle(fill_color = '#FF8C00', line_width = 2)
        config = DrawingConfig(mode = 'draw_circle', style = style)
        result = config.to_dict()
        assert result['mode'] == 'draw_circle'
        assert result['style'] == {'fillColor': [255, 140, 0], 'lineWidth': 2}

    def test_no_style_omitted(self):
        config = DrawingConfig(mode = 'draw_line')
        result = config.to_dict()
        assert 'style' not in result

    def test_delete_selected_true(self):
        config = DrawingConfig(mode = 'modify', delete_selected = True)
        result = config.to_dict()
        assert result['deleteSelected'] is True

    def test_delete_selected_false_omitted(self):
        config = DrawingConfig(mode = 'modify', delete_selected = False)
        result = config.to_dict()
        assert 'deleteSelected' not in result


class TestEmptyFeatureCollection:
    def test_structure(self):
        assert EMPTY_FEATURE_COLLECTION['type'] == 'FeatureCollection'
        assert EMPTY_FEATURE_COLLECTION['features'] == []
