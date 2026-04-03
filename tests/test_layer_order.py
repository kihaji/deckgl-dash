"""Unit tests for layer ordering feature."""
from deckgl_dash.component import DeckGL
from deckgl_dash.layers import GeoJsonLayer, ScatterplotLayer


class TestLayerOrderProp:
    """Tests for the layerOrder prop on DeckGL component."""

    def test_default_layer_order_is_none(self):
        comp = DeckGL(id = "map", layers = [])
        assert comp.layerOrder is None

    def test_layer_order_accepts_list_of_strings(self):
        comp = DeckGL(id = "map", layers = [], layer_order = ["a", "b", "c"])
        assert comp.layerOrder == ["a", "b", "c"]

    def test_layer_order_empty_list(self):
        comp = DeckGL(id = "map", layers = [], layer_order = [])
        assert comp.layerOrder == []

    def test_layer_order_with_layers(self):
        layers = [
            GeoJsonLayer(id = "polygons", data = []),
            ScatterplotLayer(id = "points", data = []),
        ]
        comp = DeckGL(id = "map", layers = layers, layer_order = ["points", "polygons"])
        assert comp.layerOrder == ["points", "polygons"]
        assert len(comp.layers) == 2

    def test_layer_order_independent_of_layer_data(self):
        comp = DeckGL(
            id = "map",
            layers = [GeoJsonLayer(id = "geo", data = [])],
            layer_data = {"geo": [{"type": "Feature"}]},
            layer_order = ["geo"],
        )
        assert comp.layerOrder == ["geo"]
        assert comp.layerData == {"geo": [{"type": "Feature"}]}

    def test_layer_order_converts_tuple_to_list(self):
        comp = DeckGL(id = "map", layers = [], layer_order = ("a", "b"))
        assert comp.layerOrder == ["a", "b"]
        assert isinstance(comp.layerOrder, list)
