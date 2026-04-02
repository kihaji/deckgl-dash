"""Tests for deckgl_dash.coordinates module."""
import pytest
from deckgl_dash.coordinates import CoordinateConverter


class TestCoordinateConverterInit:
    """Tests for CoordinateConverter construction."""

    def test_basic_construction(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        assert coord.longitude == -122.4194
        assert coord.latitude == 37.7749

    def test_from_click_info(self):
        click_info = {'picked': False, 'coordinate': [-122.4194, 37.7749]}
        coord = CoordinateConverter.from_click_info(click_info)
        assert coord.longitude == -122.4194
        assert coord.latitude == 37.7749

    def test_from_click_info_with_elevation(self):
        click_info = {'picked': True, 'coordinate': [-122.4194, 37.7749, 100.0]}
        coord = CoordinateConverter.from_click_info(click_info)
        assert coord.longitude == -122.4194
        assert coord.latitude == 37.7749

    def test_from_click_info_none_raises(self):
        with pytest.raises(ValueError):
            CoordinateConverter.from_click_info(None)  # type: ignore[arg-type]

    def test_from_click_info_no_coordinate_raises(self):
        with pytest.raises(ValueError):
            CoordinateConverter.from_click_info({'picked': False, 'coordinate': None})

    def test_longitude_out_of_range(self):
        with pytest.raises(ValueError):
            CoordinateConverter(181, 0)

    def test_latitude_out_of_range(self):
        with pytest.raises(ValueError):
            CoordinateConverter(0, 91)


class TestDecimalDegrees:
    """Tests for DD output."""

    def test_northeast(self):
        coord = CoordinateConverter(2.3522, 48.8566)
        assert coord.dd == "48.856600 N, 2.352200 E"

    def test_southwest(self):
        coord = CoordinateConverter(-43.1729, -22.9068)
        assert coord.dd == "22.906800 S, 43.172900 W"

    def test_dd_tuple(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        assert coord.dd_tuple == (37.7749, -122.4194)

    def test_origin(self):
        coord = CoordinateConverter(0, 0)
        assert coord.dd == "0.000000 N, 0.000000 E"


class TestDMS:
    """Tests for DMS output."""

    def test_san_francisco(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        dms = coord.dms
        assert "37" in dms and "N" in dms
        assert "122" in dms and "W" in dms

    def test_dms_precision(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        dms_4 = coord.dms_precision(4)
        # 4 decimal places on seconds
        assert "N" in dms_4 and "W" in dms_4

    def test_southern_hemisphere(self):
        coord = CoordinateConverter(151.2093, -33.8688)
        dms = coord.dms
        assert "S" in dms and "E" in dms

    def test_known_conversion(self):
        # 45.0 degrees should be exactly 45° 0' 0.00"
        coord = CoordinateConverter(90.0, 45.0)
        dms = coord.dms
        assert '45\u00b0 0\' 0.00" N' in dms
        assert '90\u00b0 0\' 0.00" E' in dms


class TestUTM:
    """Tests for UTM output (requires pyproj)."""

    @pytest.fixture(autouse = True)
    def _skip_without_pyproj(self):
        pytest.importorskip("pyproj")

    def test_san_francisco(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        utm = coord.utm
        assert utm.startswith("10S")

    def test_southern_hemisphere(self):
        coord = CoordinateConverter(151.2093, -33.8688)
        utm = coord.utm
        assert "H" in utm or "G" in utm  # Southern hemisphere zone letters

    def test_format_structure(self):
        coord = CoordinateConverter(-73.9857, 40.7484)
        utm = coord.utm
        parts = utm.split()
        assert len(parts) == 3  # zone, easting, northing


class TestMGRS:
    """Tests for MGRS output (requires mgrs)."""

    @pytest.fixture(autouse = True)
    def _skip_without_mgrs(self):
        pytest.importorskip("mgrs")

    def test_san_francisco(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        mgrs_str = coord.mgrs
        assert mgrs_str.startswith("10S")

    def test_precision_default_is_5(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        mgrs_5 = coord.mgrs
        mgrs_explicit = coord.mgrs_precision(5)
        assert mgrs_5 == mgrs_explicit

    def test_precision_1(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        mgrs_1 = coord.mgrs_precision(1)
        mgrs_5 = coord.mgrs_precision(5)
        assert len(mgrs_1) < len(mgrs_5)

    def test_invalid_precision(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        with pytest.raises(ValueError):
            coord.mgrs_precision(6)


class TestAsDict:
    """Tests for as_dict output."""

    def test_default_keys(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        d = coord.as_dict()
        assert set(d.keys()) == {'longitude', 'latitude', 'dd', 'dd_tuple', 'dms'}

    def test_with_utm(self):
        pytest.importorskip("pyproj")
        coord = CoordinateConverter(-122.4194, 37.7749)
        d = coord.as_dict(include_utm = True)
        assert 'utm' in d

    def test_with_mgrs(self):
        pytest.importorskip("mgrs")
        coord = CoordinateConverter(-122.4194, 37.7749)
        d = coord.as_dict(include_mgrs = True)
        assert 'mgrs' in d


class TestRepr:
    def test_repr(self):
        coord = CoordinateConverter(-122.4194, 37.7749)
        assert "CoordinateConverter" in repr(coord)
        assert "-122.4194" in repr(coord)
        assert "37.7749" in repr(coord)
