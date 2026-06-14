"""Tests for the time-filter helpers, layer serialization, and component passthrough."""
import pytest

from deckgl_dash import DeckGL, compute_time_domain, build_time_filter
from deckgl_dash.layers import ScatterplotLayer, GeoJsonLayer, PathLayer, ArcLayer, IconLayer, HeatmapLayer


class TestComputeTimeDomain:
    def test_list_of_dicts_key(self):
        data = [{"t": 5}, {"t": 1}, {"t": 9}, {"t": 3}]
        assert compute_time_domain(data, "t") == [1.0, 9.0]

    def test_dotted_path(self):
        data = [{"properties": {"t": 10}}, {"properties": {"t": 2}}]
        assert compute_time_domain(data, "properties.t") == [2.0, 10.0]

    def test_callable_accessor(self):
        data = [{"a": {"b": 4}}, {"a": {"b": 7}}]
        assert compute_time_domain(data, lambda i: i["a"]["b"]) == [4.0, 7.0]

    def test_geojson_feature_collection(self):
        fc = {"type": "FeatureCollection", "features": [
            {"properties": {"t": 100}}, {"properties": {"t": 50}}, {"properties": {"t": 75}}]}
        assert compute_time_domain(fc, "properties.t") == [50.0, 100.0]

    def test_single_row_min_equals_max(self):
        assert compute_time_domain([{"t": 42}], "t") == [42.0, 42.0]

    def test_ignores_non_numeric_and_missing(self):
        data = [{"t": 5}, {"t": None}, {"t": "x"}, {"other": 1}, {"t": 8}]
        assert compute_time_domain(data, "t") == [5.0, 8.0]

    def test_ignores_bool(self):
        # bool is an int subclass; it must not be treated as a time value.
        data = [{"t": True}, {"t": 3}, {"t": 9}]
        assert compute_time_domain(data, "t") == [3.0, 9.0]

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            compute_time_domain([], "t")

    def test_all_non_numeric_raises(self):
        with pytest.raises(ValueError):
            compute_time_domain([{"t": None}, {"t": "nope"}], "t")

    def test_bad_accessor_type_raises(self):
        with pytest.raises(TypeError):
            compute_time_domain([{"t": 1}], 123)  # type: ignore[arg-type]


class TestBuildTimeFilter:
    def test_defaults(self):
        tf = build_time_filter([0, 100], 10)
        assert tf["domain"] == [0.0, 100.0]
        assert tf["window"] == 10
        assert tf["current"] == 10  # domain[0] + window
        assert tf["speed"] == pytest.approx(100 / 20.0)  # full sweep in ~20s
        assert tf["playing"] is False
        assert tf["loop"] is True

    def test_none_values_stripped(self):
        tf = build_time_filter([0, 100], 10)
        assert "softEdge" not in tf
        assert "layerIds" not in tf
        assert "nonce" not in tf

    def test_explicit_overrides_preserved(self):
        tf = build_time_filter([0, 100], 10, current=42, playing=True, speed=3.5,
                               loop=False, soft_edge=2.0, layer_ids=["a", "b"], nonce=7)
        assert tf["current"] == 42
        assert tf["playing"] is True
        assert tf["speed"] == 3.5
        assert tf["loop"] is False
        assert tf["softEdge"] == 2.0
        assert tf["layerIds"] == ["a", "b"]
        assert tf["nonce"] == 7


class TestLayerFilterSerialization:
    def test_scatterplot_auto_attaches_extension(self):
        d = ScatterplotLayer(id="p", data=[], get_position="@@=coordinates", get_filter_value="@@=t").to_dict()
        assert d["getFilterValue"] == "@@=t"
        assert d["extensions"] == ["DataFilterExtension"]

    def test_no_filter_value_no_extension(self):
        d = ScatterplotLayer(id="p", data=[], get_position="@@=coordinates").to_dict()
        assert "extensions" not in d
        assert "getFilterValue" not in d

    def test_explicit_extensions_not_overwritten(self):
        d = ScatterplotLayer(id="p", data=[], get_filter_value="@@=t",
                             extensions=["SomethingElse"]).to_dict()
        assert d["extensions"] == ["SomethingElse"]

    def test_filter_range_and_soft_range_serialize(self):
        d = ScatterplotLayer(id="p", data=[], get_filter_value="@@=t",
                             filter_range=[0, 10], filter_soft_range=[1, 9], filter_enabled=True).to_dict()
        assert d["filterRange"] == [0, 10]
        assert d["filterSoftRange"] == [1, 9]
        assert d["filterEnabled"] is True

    @pytest.mark.parametrize("layer_cls", [GeoJsonLayer, PathLayer, ArcLayer, IconLayer])
    def test_other_layers_attach_extension(self, layer_cls):
        d = layer_cls(id="x", data=[], get_filter_value="@@=t").to_dict()
        assert d["getFilterValue"] == "@@=t"
        assert d["extensions"] == ["DataFilterExtension"]

    def test_aggregation_layer_attaches_when_requested(self):
        # HeatmapLayer has no explicit param but the kwargs path + central to_dict still work.
        d = HeatmapLayer(id="h", data=[], get_position="@@=coordinates", get_filter_value="@@=t").to_dict()
        assert d["extensions"] == ["DataFilterExtension"]

    def test_directed_path_layer_keeps_type_and_attaches_extension(self):
        # show_direction => DirectedPathLayer composite; the extension must still attach so
        # the line and arrow sublayers filter together.
        d = PathLayer(id="trips", data=[], get_path="@@=path", get_filter_value="@@=t",
                      show_direction=True, arrow_spacing=55).to_dict()
        assert d["@@type"] == "DirectedPathLayer"
        assert d["getFilterValue"] == "@@=t"
        assert d["extensions"] == ["DataFilterExtension"]


class TestTimeFilterPassthrough:
    def test_time_filter_round_trips(self):
        tf = build_time_filter([0, 100], 10, playing=True)
        comp = DeckGL(id="map", time_filter=tf)
        assert comp.timeFilter == tf

    def test_no_time_filter_by_default(self):
        comp = DeckGL(id="map")
        assert getattr(comp, "timeFilter", None) is None

    def test_current_time_output_prop(self):
        comp = DeckGL(id="map", current_time=12.5)
        assert comp.currentTime == 12.5
