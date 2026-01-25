"""Color scale utilities for deckgl-dash.

Provides Pythonic helpers for data-driven color mapping using chroma.js scales.

Example:
    >>> from deckgl_dash.colors import ColorScale, color_range_from_scale
    >>>
    >>> # Fluent API for complex configurations
    >>> scale = ColorScale('viridis').domain(0, 100).alpha(180).reverse()
    >>> get_fill_color = scale.accessor('properties.count')
    >>>
    >>> # Simple usage with auto-domain
    >>> get_fill_color = ColorScale('plasma').accessor('properties.value')
    >>>
    >>> # For aggregation layers
    >>> color_range = color_range_from_scale('viridis', 6)
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Union

# Available color scales from chroma.js
AVAILABLE_SCALES: Tuple[str, ...] = (
    # Sequential
    'OrRd', 'PuBu', 'BuPu', 'Oranges', 'BuGn', 'YlOrBr', 'YlGn', 'Reds',
    'RdPu', 'Greens', 'YlGnBu', 'Purples', 'GnBu', 'Greys', 'YlOrRd',
    'PuRd', 'Blues', 'PuBuGn',
    # Diverging
    'Spectral', 'RdYlGn', 'RdBu', 'PiYG', 'PRGn', 'RdYlBu', 'BrBG', 'RdGy', 'PuOr',
    # Perceptually uniform
    'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'turbo',
)

# Color definitions for Python-side scale generation (subset for color_range_from_scale)
_SCALE_COLORS = {
    'viridis': ['#440154', '#482878', '#3e4a89', '#31688e', '#26828e', '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725'],
    'plasma': ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'],
    'inferno': ['#000004', '#1b0c41', '#4a0c6b', '#781c6d', '#a52c60', '#cf4446', '#ed6925', '#fb9b06', '#f7d13d', '#fcffa4'],
    'magma': ['#000004', '#180f3d', '#440f76', '#721f81', '#9e2f7f', '#cd4071', '#f1605d', '#fd9668', '#feca8d', '#fcfdbf'],
    'cividis': ['#00204d', '#00336f', '#39486b', '#575c6d', '#6f7174', '#87877b', '#a09e81', '#bab587', '#d6cd8e', '#ffe945'],
    'turbo': ['#30123b', '#4662d7', '#35aaf9', '#1ae4b6', '#72fe5e', '#c8ef34', '#faba39', '#f66b19', '#ca2a04', '#7a0403'],
    'OrRd': ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000'],
    'YlGnBu': ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0', '#225ea8', '#253494', '#081d58'],
    'RdYlBu': ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695'],
    'Spectral': ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2'],
    'Blues': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
    'Reds': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
    'Greens': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
}


class ColorScale:
    """Fluent API for building @@scale accessor strings.

    Example:
        >>> scale = ColorScale('viridis').domain(0, 100).alpha(180).log()
        >>> accessor = scale.accessor('properties.count')
        >>> # Returns: '@@scale(viridis:log, properties.count, 0, 100, 180)'
    """

    def __init__(self, scale_name: str):
        """Initialize color scale.

        Args:
            scale_name: Name of the chroma.js scale (e.g., 'viridis', 'plasma', 'OrRd')
        """
        if scale_name not in AVAILABLE_SCALES:
            raise ValueError(f"Unknown scale '{scale_name}'. Available scales: {', '.join(AVAILABLE_SCALES)}")
        self._scale_name = scale_name
        self._min: Optional[float] = None
        self._max: Optional[float] = None
        self._alpha: Optional[int] = None
        self._reverse: bool = False
        self._log: bool = False
        self._sqrt: bool = False

    def domain(self, min_val: float, max_val: float) -> 'ColorScale':
        """Set explicit domain (min/max values). If not set, auto-detected from data.

        Args:
            min_val: Minimum value for the scale
            max_val: Maximum value for the scale

        Returns:
            Self for chaining
        """
        if min_val >= max_val:
            raise ValueError(f"min_val ({min_val}) must be less than max_val ({max_val})")
        self._min = min_val
        self._max = max_val
        return self

    def alpha(self, value: int) -> 'ColorScale':
        """Set alpha (transparency) channel. Default is 255 (fully opaque).

        Args:
            value: Alpha value 0-255

        Returns:
            Self for chaining
        """
        if not 0 <= value <= 255:
            raise ValueError(f"Alpha must be 0-255, got {value}")
        self._alpha = value
        return self

    def reverse(self) -> 'ColorScale':
        """Reverse the color scale direction.

        Returns:
            Self for chaining
        """
        self._reverse = True
        return self

    def log(self) -> 'ColorScale':
        """Use logarithmic interpolation. Good for exponential data distributions.

        Note: Requires positive values. Min domain will be clamped to 0.001 if <= 0.

        Returns:
            Self for chaining
        """
        self._log = True
        self._sqrt = False  # Mutually exclusive
        return self

    def sqrt(self) -> 'ColorScale':
        """Use square root interpolation. Less extreme than log scale.

        Returns:
            Self for chaining
        """
        self._sqrt = True
        self._log = False  # Mutually exclusive
        return self

    def accessor(self, property_path: str) -> str:
        """Generate the @@scale accessor string.

        Args:
            property_path: Path to the data property (e.g., 'properties.count', 'value')

        Returns:
            @@scale accessor string for use with deck.gl layers
        """
        # Build scale name with modifiers
        scale_spec = self._scale_name
        modifiers = []
        if self._log:
            modifiers.append('log')
        if self._sqrt:
            modifiers.append('sqrt')
        if self._reverse:
            modifiers.append('reverse')
        if modifiers:
            scale_spec = f"{scale_spec}:{':'.join(modifiers)}"

        # Build parameter list
        params = [scale_spec, property_path]
        if self._min is not None and self._max is not None:
            params.append(str(self._min))
            params.append(str(self._max))
            if self._alpha is not None:
                params.append(str(self._alpha))
        elif self._alpha is not None:
            # Alpha without domain - need placeholder for domain
            # Use empty strings which will be parsed as null in JS
            params.extend(['', '', str(self._alpha)])

        return f"@@scale({', '.join(params)})"

    def __repr__(self) -> str:
        mods = []
        if self._log:
            mods.append('log')
        if self._sqrt:
            mods.append('sqrt')
        if self._reverse:
            mods.append('reverse')
        mod_str = f":{':'.join(mods)}" if mods else ''
        domain_str = f", domain=({self._min}, {self._max})" if self._min is not None else ''
        alpha_str = f", alpha={self._alpha}" if self._alpha is not None else ''
        return f"ColorScale('{self._scale_name}{mod_str}'{domain_str}{alpha_str})"


def color_range_from_scale(scale_name: str, steps: int = 6, reverse: bool = False) -> List[List[int]]:
    """Generate a discrete color range array from a chroma scale.

    Useful for aggregation layers that need a colorRange prop (HexagonLayer, GridLayer, etc.).

    Args:
        scale_name: Name of the chroma.js scale (e.g., 'viridis', 'plasma')
        steps: Number of colors to generate (default 6)
        reverse: If True, reverse the color order

    Returns:
        List of [r, g, b] color arrays

    Example:
        >>> color_range_from_scale('viridis', 6)
        [[68, 1, 84], [59, 82, 139], [33, 144, 140], [93, 201, 99], [253, 231, 37]]
    """
    if scale_name not in _SCALE_COLORS:
        # Fall back to a default if not in our Python-side definitions
        if scale_name not in AVAILABLE_SCALES:
            raise ValueError(f"Unknown scale '{scale_name}'. Available scales: {', '.join(AVAILABLE_SCALES)}")
        # Use viridis as fallback for scales we don't have Python definitions for
        scale_name = 'viridis'

    colors = _SCALE_COLORS[scale_name]
    n = len(colors)

    # Interpolate to get exactly 'steps' colors
    result = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        idx = t * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo

        # Parse hex colors and interpolate
        c1 = _hex_to_rgb(colors[lo])
        c2 = _hex_to_rgb(colors[hi])
        r = int(c1[0] + frac * (c2[0] - c1[0]))
        g = int(c1[1] + frac * (c2[1] - c1[1]))
        b = int(c1[2] + frac * (c2[2] - c1[2]))
        result.append([r, g, b])

    if reverse:
        result = result[::-1]

    return result


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
