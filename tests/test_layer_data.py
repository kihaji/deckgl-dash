"""Unit tests for the layerData prop on the DeckGL component."""
from deckgl_dash import DeckGL


class TestLayerDataProp:
    """Tests for the layer_data parameter on DeckGL."""

    def test_default_is_none(self):
        comp = DeckGL(id = "map")
        assert comp.layerData is None

    def test_accepts_layer_data_kwarg(self):
        data = {"hexagons": [{"coordinates": [0, 0]}]}
        comp = DeckGL(id = "map", layer_data = data)
        assert comp.layerData == data

    def test_single_layer_id(self):
        data = {"scatter": [1, 2, 3]}
        comp = DeckGL(id = "map", layer_data = data)
        assert comp.layerData == {"scatter": [1, 2, 3]}

    def test_multiple_layer_ids(self):
        data = {"hexagons": [{"x": 1}], "scatter": [{"y": 2}], "arcs": "https://example.com/data.json"}
        comp = DeckGL(id = "map", layer_data = data)
        assert comp.layerData == data
        assert len(comp.layerData) == 3

    def test_empty_dict(self):
        comp = DeckGL(id = "map", layer_data = {})
        assert comp.layerData == {}

    def test_data_values_can_be_any_type(self):
        data = {
            "geojson": {"type": "FeatureCollection", "features": []},
            "scatter": [{"pos": [0, 0]}, {"pos": [1, 1]}],
            "remote": "https://example.com/data.csv",
        }
        comp = DeckGL(id = "map", layer_data = data)
        assert comp.layerData["geojson"]["type"] == "FeatureCollection"
        assert len(comp.layerData["scatter"]) == 2
        assert comp.layerData["remote"] == "https://example.com/data.csv"

    def test_layer_data_independent_of_layers(self):
        layers = [{"@@type": "ScatterplotLayer", "id": "scatter", "data": []}]
        layer_data = {"scatter": [{"pos": [0, 0]}]}
        comp = DeckGL(id = "map", layers = layers, layer_data = layer_data)
        assert comp.layers == layers
        assert comp.layerData == layer_data
