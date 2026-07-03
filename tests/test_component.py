"""Tests for deckgl_dash/component.py — the snake_case wrapper every user touches (issue #28)."""
import pytest
from deckgl_dash import DeckGL, DeckGLBase, DrawingConfig
from deckgl_dash.layers import ScatterplotLayer, GeoJsonLayer

VIEW = {'longitude': -122.4, 'latitude': 37.8, 'zoom': 11}

# Every snake_case wrapper kwarg and the camelCase prop it must land on, with a representative value.
PROP_FORWARDING = [
    ('layer_data', 'layerData', {'lyr': [{'a': 1}]}),
    ('layer_order', 'layerOrder', ['a', 'b']),
    ('initial_view_state', 'initialViewState', VIEW),
    ('view_state', 'viewState', VIEW),
    ('fit_bounds', 'fitBounds', {'bounds': [[-1, -1], [1, 1]], 'padding': 10}),
    ('controller', 'controller', {'dragPan': False}),
    ('enable_events', 'enableEvents', ['click', 'hover']),
    ('tooltip', 'tooltip', {'html': '<b>{name}</b>'}),
    ('style', 'style', {'height': '500px'}),
    ('maplibre_config', 'maplibreConfig', {'style': 'https://example.com/style.json'}),
    ('map_style_loaded', 'mapStyleLoaded', True),
    ('click_info', 'clickInfo', {'picked': True}),
    ('hover_info', 'hoverInfo', {'picked': False}),
    ('data_load_info', 'dataLoadInfo', {'layerId': 'x', 'featureCount': 1}),
    ('data_load_error', 'dataLoadError', {'layerId': 'x', 'error': 'nope'}),
    ('drawing_config', 'drawingConfig', {'mode': 'polygon'}),
    ('drawing_features', 'drawingFeatures', {'type': 'FeatureCollection', 'features': []}),
    ('drawing_event', 'drawingEvent', {'type': 'addFeature'}),
    ('time_filter', 'timeFilter', {'domain': [0, 10], 'window': 2}),
    ('current_time', 'currentTime', 4.2),
]


class TestSnakeCaseForwarding:
    """Every wrapper kwarg must forward to its camelCase prop unchanged."""

    @pytest.mark.parametrize('snake, camel, value', PROP_FORWARDING, ids = [p[0] for p in PROP_FORWARDING])
    def test_forwarding(self, snake, camel, value):
        comp = DeckGL(id = 'map', **{snake: value})
        assert getattr(comp, camel) == value

    def test_id_and_layers_forward_directly(self):
        comp = DeckGL(id = 'map', layers = [{'@@type': 'TileLayer', 'id': 't'}])
        assert comp.id == 'map'
        assert comp.layers == [{'@@type': 'TileLayer', 'id': 't'}]

    def test_layer_order_tuple_becomes_list(self):
        comp = DeckGL(id = 'map', layer_order = ('a', 'b'))
        assert comp.layerOrder == ['a', 'b']

    def test_omitted_props_forward_as_none(self):
        # The wrapper forwards every prop explicitly, so omitted kwargs materialize as None
        comp = DeckGL(id = 'map')
        assert comp.timeFilter is None
        assert comp.maplibreConfig is None


class TestLayerConversion:
    """BaseLayer objects convert via process_layers; camelCase dicts pass through."""

    def test_baselayer_converted_to_dict(self):
        comp = DeckGL(id = 'map', layers = [ScatterplotLayer(id = 'pts', data = [], get_radius = 5)])
        assert comp.layers == [{'@@type': 'ScatterplotLayer', 'id': 'pts', 'data': [], 'getRadius': 5}]

    def test_dicts_pass_through_untouched(self):
        raw = {'@@type': 'GeoJsonLayer', 'id': 'g', 'getFillColor': [1, 2, 3], 'customCamel': True}
        comp = DeckGL(id = 'map', layers = [raw])
        assert comp.layers[0] is raw

    def test_mixed_layers(self):
        raw = {'@@type': 'TileLayer', 'id': 't'}
        comp = DeckGL(id = 'map', layers = [GeoJsonLayer(id = 'g', data = []), raw])
        assert comp.layers[0]['@@type'] == 'GeoJsonLayer'
        assert comp.layers[1] is raw

    def test_invalid_layer_type_raises(self):
        with pytest.raises(TypeError, match = 'BaseLayer or dict'):
            DeckGL(id = 'map', layers = ['not-a-layer'])


class TestDrawingConfigSerialization:
    def test_drawing_config_object_serialized(self):
        comp = DeckGL(id = 'map', drawing_config = DrawingConfig(mode = 'draw_polygon'))
        assert isinstance(comp.drawingConfig, dict)
        assert comp.drawingConfig['mode'] == 'draw_polygon'

    def test_drawing_config_dict_passthrough(self):
        cfg = {'mode': 'point', 'deleteSelected': False}
        comp = DeckGL(id = 'map', drawing_config = cfg)
        assert comp.drawingConfig == cfg


class TestErrorBehavior:
    def test_unknown_kwarg_raises_typeerror(self):
        with pytest.raises(TypeError):
            DeckGL(id = 'map', not_a_real_prop = 123)

    def test_camelcase_duplicate_of_wrapped_prop_raises(self):
        # The wrapper forwards every wrapped prop itself, so passing the camelCase
        # name through **kwargs collides ("got multiple values") rather than merging
        with pytest.raises(TypeError):
            DeckGL(id = 'map', clickInfo = {'picked': True})


class TestWrapperIsDashComponent:
    def test_subclasses_generated_component(self):
        assert issubclass(DeckGL, DeckGLBase)

    def test_to_plotly_json_shape(self):
        comp = DeckGL(id = 'map', layers = [], initial_view_state = VIEW)
        j = comp.to_plotly_json()
        assert j['type'] == 'DeckGL'
        assert j['namespace'] == 'deckgl_dash'
        assert j['props']['initialViewState'] == VIEW
