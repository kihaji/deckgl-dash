"""Tests for the feature_list_highlight_demo example's pure data builders."""
import os
import sys

# Make the repo root importable so `examples` resolves under pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.feature_list_highlight_demo import (  # noqa: E402
    build_regions_fc, build_routes, REGIONS, ROUTES,
)


def _selected_names(features_or_routes):
    return [f["properties"]["name"] for f in features_or_routes if f["properties"]["selected"]]


class TestBuildRegionsFc:
    def test_structure(self):
        fc = build_regions_fc()
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == len(REGIONS)
        feat = fc["features"][0]
        assert feat["type"] == "Feature"
        assert feat["geometry"]["type"] == "Polygon"
        # Each Polygon is a list of rings; one ring here.
        assert isinstance(feat["geometry"]["coordinates"][0], list)
        assert set(feat["properties"]) == {"name", "color", "selected"}

    def test_exactly_one_selected(self):
        name = REGIONS[1]["name"]
        fc = build_regions_fc(name)
        assert _selected_names(fc["features"]) == [name]

    def test_none_selected_by_default(self):
        assert _selected_names(build_regions_fc()["features"]) == []
        assert _selected_names(build_regions_fc(None)["features"]) == []

    def test_unknown_name_selects_nothing(self):
        assert _selected_names(build_regions_fc("Nonexistent")["features"]) == []


class TestBuildRoutes:
    def test_structure(self):
        routes = build_routes()
        assert len(routes) == len(ROUTES)
        r = routes[0]
        assert "path" in r and isinstance(r["path"], list)
        assert set(r["properties"]) == {"name", "color", "selected"}

    def test_exactly_one_selected(self):
        name = ROUTES[0]["name"]
        assert _selected_names(build_routes(name)) == [name]

    def test_region_name_selects_no_route(self):
        # Region and route names are disjoint, so a region name selects no route.
        assert _selected_names(build_routes(REGIONS[0]["name"])) == []
