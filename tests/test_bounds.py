"""Tests for compute_bounds and the fit_bounds component passthrough."""
import pytest

from deckgl_dash import DeckGL, compute_bounds


class TestComputeBounds:
    def test_point_dicts(self):
        data = [{"coordinates": [-122.4, 37.8]}, {"coordinates": [-122.3, 37.9]}]
        assert compute_bounds(data) == [[-122.4, 37.8], [-122.3, 37.9]]

    def test_raw_lonlat_pairs(self):
        assert compute_bounds([[-1, -2], [3, 4]]) == [[-1.0, -2.0], [3.0, 4.0]]

    def test_paths(self):
        data = [{"path": [[0, 0], [10, 5]]}, {"path": [[-5, 2], [1, 1]]}]
        assert compute_bounds(data) == [[-5.0, 0.0], [10.0, 5.0]]

    def test_polygon(self):
        data = [{"polygon": [[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]]}]
        assert compute_bounds(data) == [[-1.0, -1.0], [1.0, 1.0]]

    def test_geojson_feature_collection(self):
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": {
                "type": "Polygon", "coordinates": [[
                    [-122.5, 37.7], [-122.0, 37.7], [-122.0, 38.0], [-122.5, 38.0], [-122.5, 37.7]]]}},
            {"type": "Feature", "properties": {}, "geometry": {
                "type": "Point", "coordinates": [-121.8, 38.2]}},
        ]}
        assert compute_bounds(fc) == [[-122.5, 37.7], [-121.8, 38.2]]

    def test_degenerate_single_point(self):
        # Min == max on both axes; the React layer falls back to a sane zoom.
        assert compute_bounds([{"coordinates": [-122.4, 37.8]}]) == [[-122.4, 37.8], [-122.4, 37.8]]

    def test_custom_accessor(self):
        data = [{"p": [5, 6]}, {"p": [7, 8]}]
        assert compute_bounds(data, get_coordinates=lambda i: i["p"]) == [[5.0, 6.0], [7.0, 8.0]]

    def test_accessor_over_feature_collection(self):
        fc = {"features": [{"loc": [1, 2]}, {"loc": [3, 4]}]}
        assert compute_bounds(fc, get_coordinates=lambda f: f["loc"]) == [[1.0, 2.0], [3.0, 4.0]]

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            compute_bounds([])

    def test_ignores_non_coordinate_numbers(self):
        # `value` must not be mistaken for a coordinate.
        data = [{"coordinates": [-10, 20], "value": 999}]
        assert compute_bounds(data) == [[-10.0, 20.0], [-10.0, 20.0]]


class TestFitBoundsPassthrough:
    def test_fit_bounds_round_trips(self):
        fb = {"bounds": [[-1, -2], [3, 4]], "padding": 40, "maxZoom": 15}
        comp = DeckGL(id="map", fit_bounds=fb)
        assert comp.fitBounds == fb

    def test_fit_bounds_from_compute_bounds(self):
        bounds = compute_bounds([[0, 0], [10, 10]])
        comp = DeckGL(id="map", fit_bounds={"bounds": bounds, "padding": 20})
        assert comp.fitBounds == {"bounds": [[0.0, 0.0], [10.0, 10.0]], "padding": 20}

    def test_no_fit_bounds_by_default(self):
        comp = DeckGL(id="map")
        assert getattr(comp, "fitBounds", None) is None
