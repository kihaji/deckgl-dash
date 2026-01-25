"""Tests for dash_deckgl.colors module."""
import pytest
from dash_deckgl.colors import ColorScale, color_range_from_scale, AVAILABLE_SCALES


class TestColorScale:
    """Tests for ColorScale class."""

    def test_basic_accessor(self):
        """Test basic accessor string generation."""
        scale = ColorScale('viridis')
        result = scale.accessor('properties.count')
        assert result == '@@scale(viridis, properties.count)'

    def test_with_domain(self):
        """Test accessor with explicit domain."""
        scale = ColorScale('plasma').domain(0, 100)
        result = scale.accessor('properties.value')
        assert result == '@@scale(plasma, properties.value, 0, 100)'

    def test_with_alpha(self):
        """Test accessor with alpha channel."""
        scale = ColorScale('OrRd').domain(0, 1000).alpha(200)
        result = scale.accessor('properties.value')
        assert result == '@@scale(OrRd, properties.value, 0, 1000, 200)'

    def test_reverse_modifier(self):
        """Test reversed scale modifier."""
        scale = ColorScale('Spectral').reverse().domain(-10, 40)
        result = scale.accessor('properties.temp')
        assert result == '@@scale(Spectral:reverse, properties.temp, -10, 40)'

    def test_log_modifier(self):
        """Test logarithmic scale modifier."""
        scale = ColorScale('viridis').log()
        result = scale.accessor('properties.population')
        assert result == '@@scale(viridis:log, properties.population)'

    def test_sqrt_modifier(self):
        """Test square root scale modifier."""
        scale = ColorScale('magma').sqrt().domain(0, 10000)
        result = scale.accessor('properties.area')
        assert result == '@@scale(magma:sqrt, properties.area, 0, 10000)'

    def test_combined_modifiers(self):
        """Test combined log and reverse modifiers."""
        scale = ColorScale('plasma').log().reverse().domain(1, 1000)
        result = scale.accessor('properties.value')
        assert result == '@@scale(plasma:log:reverse, properties.value, 1, 1000)'

    def test_log_and_sqrt_mutually_exclusive(self):
        """Test that log and sqrt are mutually exclusive (last one wins)."""
        scale = ColorScale('viridis').log().sqrt()  # sqrt should win
        result = scale.accessor('properties.x')
        assert ':sqrt' in result
        assert ':log' not in result

        scale2 = ColorScale('viridis').sqrt().log()  # log should win
        result2 = scale2.accessor('properties.x')
        assert ':log' in result2
        assert ':sqrt' not in result2

    def test_invalid_scale_name(self):
        """Test that invalid scale names raise ValueError."""
        with pytest.raises(ValueError, match="Unknown scale"):
            ColorScale('not_a_real_scale')

    def test_invalid_domain(self):
        """Test that invalid domain (min >= max) raises ValueError."""
        scale = ColorScale('viridis')
        with pytest.raises(ValueError, match="must be less than"):
            scale.domain(100, 50)
        with pytest.raises(ValueError, match="must be less than"):
            scale.domain(50, 50)

    def test_invalid_alpha(self):
        """Test that invalid alpha values raise ValueError."""
        scale = ColorScale('viridis')
        with pytest.raises(ValueError, match="Alpha must be 0-255"):
            scale.alpha(-1)
        with pytest.raises(ValueError, match="Alpha must be 0-255"):
            scale.alpha(256)

    def test_repr(self):
        """Test string representation."""
        scale = ColorScale('viridis').domain(0, 100).log()
        repr_str = repr(scale)
        assert 'viridis' in repr_str
        assert 'log' in repr_str
        assert 'domain' in repr_str

    def test_chaining(self):
        """Test fluent API chaining returns self."""
        scale = ColorScale('viridis')
        assert scale.domain(0, 100) is scale
        assert scale.alpha(180) is scale
        assert scale.reverse() is scale
        assert scale.log() is scale


class TestColorRangeFromScale:
    """Tests for color_range_from_scale function."""

    def test_basic_generation(self):
        """Test basic color range generation."""
        colors = color_range_from_scale('viridis', 6)
        assert len(colors) == 6
        assert all(len(c) == 3 for c in colors)
        assert all(all(0 <= v <= 255 for v in c) for c in colors)

    def test_different_steps(self):
        """Test different step counts."""
        for steps in [3, 5, 8, 10]:
            colors = color_range_from_scale('plasma', steps)
            assert len(colors) == steps

    def test_reverse(self):
        """Test reversed color range."""
        normal = color_range_from_scale('viridis', 5)
        reversed_colors = color_range_from_scale('viridis', 5, reverse = True)
        assert normal == reversed_colors[::-1]

    def test_invalid_scale(self):
        """Test that invalid scale names raise ValueError."""
        with pytest.raises(ValueError, match="Unknown scale"):
            color_range_from_scale('not_a_real_scale', 6)


class TestAvailableScales:
    """Tests for AVAILABLE_SCALES constant."""

    def test_contains_common_scales(self):
        """Test that common scales are included."""
        expected = ['viridis', 'plasma', 'inferno', 'magma', 'OrRd', 'Spectral', 'RdYlBu']
        for scale in expected:
            assert scale in AVAILABLE_SCALES

    def test_is_tuple(self):
        """Test that AVAILABLE_SCALES is immutable (tuple)."""
        assert isinstance(AVAILABLE_SCALES, tuple)
