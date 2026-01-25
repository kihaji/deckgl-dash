"""Unit tests for deckgl-dash layer helpers."""
import pytest
from deckgl_dash.layers import (
    BaseLayer, process_layers, normalize_color, to_camel_case,
    GeoJsonLayer, ScatterplotLayer, PathLayer, LineLayer, ArcLayer, IconLayer, TextLayer, PolygonLayer,
    TileLayer, MVTLayer, BitmapLayer,
    HeatmapLayer, HexagonLayer, GridLayer,
)


class TestNormalizeColor:
    """Tests for color normalization."""

    def test_rgb_list(self):
        assert normalize_color([255, 128, 0]) == [255, 128, 0]

    def test_rgba_list(self):
        assert normalize_color([255, 128, 0, 200]) == [255, 128, 0, 200]

    def test_rgb_tuple(self):
        assert normalize_color((255, 128, 0)) == [255, 128, 0]

    def test_rgba_tuple(self):
        assert normalize_color((255, 128, 0, 200)) == [255, 128, 0, 200]

    def test_hex_rgb(self):
        assert normalize_color('#FF8000') == [255, 128, 0]

    def test_hex_rgba(self):
        assert normalize_color('#FF8000C8') == [255, 128, 0, 200]

    def test_hex_short_rgb(self):
        assert normalize_color('#F80') == [255, 136, 0]

    def test_hex_short_rgba(self):
        assert normalize_color('#F80C') == [255, 136, 0, 204]

    def test_hex_lowercase(self):
        assert normalize_color('#ff8000') == [255, 128, 0]

    def test_invalid_no_hash(self):
        with pytest.raises(ValueError, match="must start with '#'"):
            normalize_color('FF8000')

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="Invalid hex color format"):
            normalize_color('#FF800')

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be a list, tuple, or hex string"):
            normalize_color(12345)

    def test_invalid_components(self):
        with pytest.raises(ValueError, match="must have 3 or 4 components"):
            normalize_color([255, 128])


class TestToCamelCase:
    """Tests for snake_case to camelCase conversion."""

    def test_simple(self):
        assert to_camel_case('get_fill_color') == 'getFillColor'

    def test_single_word(self):
        assert to_camel_case('data') == 'data'

    def test_multiple_underscores(self):
        assert to_camel_case('line_width_min_pixels') == 'lineWidthMinPixels'

    def test_already_camel(self):
        assert to_camel_case('fillColor') == 'fillColor'


class TestGeoJsonLayer:
    """Tests for GeoJsonLayer."""

    def test_basic(self):
        layer = GeoJsonLayer(id = 'test', data = 'https://example.com/data.geojson')
        d = layer.to_dict()
        assert d['@@type'] == 'GeoJsonLayer'
        assert d['id'] == 'test'
        assert d['data'] == 'https://example.com/data.geojson'

    def test_with_color_list(self):
        layer = GeoJsonLayer(id = 'test', data = [], get_fill_color = [255, 140, 0])
        d = layer.to_dict()
        assert d['getFillColor'] == [255, 140, 0]

    def test_with_color_hex(self):
        layer = GeoJsonLayer(id = 'test', data = [], get_fill_color = '#FF8C00')
        d = layer.to_dict()
        assert d['getFillColor'] == [255, 140, 0]

    def test_with_accessor_string(self):
        layer = GeoJsonLayer(id = 'test', data = [], get_fill_color = '@@=properties.color')
        d = layer.to_dict()
        assert d['getFillColor'] == '@@=properties.color'

    def test_with_all_options(self):
        layer = GeoJsonLayer(
            id = 'test', data = [],
            filled = True, stroked = True, extruded = False,
            get_fill_color = [255, 0, 0], get_line_color = '#000000',
            get_line_width = 2, pickable = True, opacity = 0.8
        )
        d = layer.to_dict()
        assert d['filled'] is True
        assert d['stroked'] is True
        assert d['extruded'] is False
        assert d['getFillColor'] == [255, 0, 0]
        assert d['getLineColor'] == [0, 0, 0]
        assert d['getLineWidth'] == 2
        assert d['pickable'] is True
        assert d['opacity'] == 0.8

    def test_extra_kwargs(self):
        layer = GeoJsonLayer(id = 'test', data = [], custom_prop = 'value')
        d = layer.to_dict()
        assert d['customProp'] == 'value'

    def test_repr(self):
        layer = GeoJsonLayer(id = 'test', data = 'url', pickable = True)
        repr_str = repr(layer)
        assert 'GeoJsonLayer' in repr_str
        assert 'test' in repr_str


class TestScatterplotLayer:
    """Tests for ScatterplotLayer."""

    def test_basic(self):
        layer = ScatterplotLayer(id = 'scatter', data = [], get_position = '@@=coordinates')
        d = layer.to_dict()
        assert d['@@type'] == 'ScatterplotLayer'
        assert d['getPosition'] == '@@=coordinates'

    def test_with_radius(self):
        layer = ScatterplotLayer(id = 'scatter', data = [], get_radius = 100, radius_min_pixels = 2, radius_max_pixels = 20)
        d = layer.to_dict()
        assert d['getRadius'] == 100
        assert d['radiusMinPixels'] == 2
        assert d['radiusMaxPixels'] == 20


class TestPathLayer:
    """Tests for PathLayer."""

    def test_basic(self):
        layer = PathLayer(id = 'path', data = [], get_path = '@@=coordinates', get_color = '#FF0000', get_width = 5)
        d = layer.to_dict()
        assert d['@@type'] == 'PathLayer'
        assert d['getPath'] == '@@=coordinates'
        assert d['getColor'] == [255, 0, 0]
        assert d['getWidth'] == 5


class TestLineLayer:
    """Tests for LineLayer."""

    def test_basic(self):
        layer = LineLayer(id = 'line', data = [], get_source_position = '@@=source', get_target_position = '@@=target')
        d = layer.to_dict()
        assert d['@@type'] == 'LineLayer'
        assert d['getSourcePosition'] == '@@=source'
        assert d['getTargetPosition'] == '@@=target'


class TestArcLayer:
    """Tests for ArcLayer."""

    def test_basic(self):
        layer = ArcLayer(
            id = 'arc', data = [],
            get_source_position = '@@=origin', get_target_position = '@@=destination',
            get_source_color = '#0080C8', get_target_color = '#C80050'
        )
        d = layer.to_dict()
        assert d['@@type'] == 'ArcLayer'
        assert d['getSourceColor'] == [0, 128, 200]
        assert d['getTargetColor'] == [200, 0, 80]


class TestIconLayer:
    """Tests for IconLayer."""

    def test_basic(self):
        layer = IconLayer(
            id = 'icons', data = [],
            get_position = '@@=coordinates', get_icon = '@@=icon',
            icon_atlas = 'https://example.com/icons.png',
            icon_mapping = {'marker': {'x': 0, 'y': 0, 'width': 128, 'height': 128}}
        )
        d = layer.to_dict()
        assert d['@@type'] == 'IconLayer'
        assert d['iconAtlas'] == 'https://example.com/icons.png'
        assert 'marker' in d['iconMapping']


class TestTextLayer:
    """Tests for TextLayer."""

    def test_basic(self):
        layer = TextLayer(id = 'text', data = [], get_position = '@@=coordinates', get_text = '@@=name', get_size = 16)
        d = layer.to_dict()
        assert d['@@type'] == 'TextLayer'
        assert d['getText'] == '@@=name'
        assert d['getSize'] == 16


class TestPolygonLayer:
    """Tests for PolygonLayer."""

    def test_basic(self):
        layer = PolygonLayer(id = 'poly', data = [], get_polygon = '@@=coordinates', get_fill_color = [255, 140, 0, 200])
        d = layer.to_dict()
        assert d['@@type'] == 'PolygonLayer'
        assert d['getPolygon'] == '@@=coordinates'
        assert d['getFillColor'] == [255, 140, 0, 200]


class TestTileLayer:
    """Tests for TileLayer."""

    def test_basic(self):
        layer = TileLayer(id = 'tiles', data = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png')
        d = layer.to_dict()
        assert d['@@type'] == 'TileLayer'
        assert d['data'] == 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

    def test_with_zoom_range(self):
        layer = TileLayer(id = 'tiles', data = 'url', min_zoom = 0, max_zoom = 19)
        d = layer.to_dict()
        assert d['minZoom'] == 0
        assert d['maxZoom'] == 19


class TestMVTLayer:
    """Tests for MVTLayer."""

    def test_basic(self):
        layer = MVTLayer(id = 'mvt', data = 'https://example.com/{z}/{x}/{y}.mvt', get_fill_color = '#FF0000')
        d = layer.to_dict()
        assert d['@@type'] == 'MVTLayer'
        assert d['getFillColor'] == [255, 0, 0]


class TestBitmapLayer:
    """Tests for BitmapLayer."""

    def test_basic(self):
        layer = BitmapLayer(id = 'bitmap', image = 'https://example.com/image.png', bounds = [-122.5, 37.5, -122.0, 38.0])
        d = layer.to_dict()
        assert d['@@type'] == 'BitmapLayer'
        assert d['image'] == 'https://example.com/image.png'
        assert d['bounds'] == [-122.5, 37.5, -122.0, 38.0]


class TestHeatmapLayer:
    """Tests for HeatmapLayer."""

    def test_basic(self):
        layer = HeatmapLayer(id = 'heatmap', data = [], get_position = '@@=coordinates', radius_pixels = 30)
        d = layer.to_dict()
        assert d['@@type'] == 'HeatmapLayer'
        assert d['radiusPixels'] == 30


class TestHexagonLayer:
    """Tests for HexagonLayer."""

    def test_basic(self):
        layer = HexagonLayer(id = 'hex', data = [], get_position = '@@=coordinates', radius = 1000, extruded = True)
        d = layer.to_dict()
        assert d['@@type'] == 'HexagonLayer'
        assert d['radius'] == 1000
        assert d['extruded'] is True


class TestGridLayer:
    """Tests for GridLayer."""

    def test_basic(self):
        layer = GridLayer(id = 'grid', data = [], get_position = '@@=coordinates', cell_size = 200, extruded = True)
        d = layer.to_dict()
        assert d['@@type'] == 'GridLayer'
        assert d['cellSize'] == 200
        assert d['extruded'] is True


class TestProcessLayers:
    """Tests for process_layers function."""

    def test_empty_list(self):
        assert process_layers([]) == []

    def test_none(self):
        assert process_layers(None) is None

    def test_dict_passthrough(self):
        layers = [{'@@type': 'GeoJsonLayer', 'id': 'test', 'data': []}]
        result = process_layers(layers)
        assert result == layers

    def test_layer_objects(self):
        layers = [
            GeoJsonLayer(id = 'geo', data = []),
            TileLayer(id = 'tile', data = 'url'),
        ]
        result = process_layers(layers)
        assert len(result) == 2
        assert result[0]['@@type'] == 'GeoJsonLayer'
        assert result[1]['@@type'] == 'TileLayer'

    def test_mixed(self):
        layers = [
            {'@@type': 'TileLayer', 'id': 'base', 'data': 'url'},
            GeoJsonLayer(id = 'geo', data = []),
        ]
        result = process_layers(layers)
        assert len(result) == 2
        assert result[0]['@@type'] == 'TileLayer'
        assert result[1]['@@type'] == 'GeoJsonLayer'

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be a BaseLayer or dict"):
            process_layers(['not a layer'])
