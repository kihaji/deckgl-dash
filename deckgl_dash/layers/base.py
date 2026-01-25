"""Base layer class for dash-deckgl Python layer helpers."""
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

# Type aliases for color values
ColorRGB = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]
ColorValue = Union[ColorRGB, ColorRGBA, List[int], str]  # RGB, RGBA, or hex string
AccessorValue = Union[ColorValue, str, int, float, bool, None]  # Static value or @@= accessor string


def normalize_color(color: ColorValue) -> List[int]:
    """Convert color to [r, g, b] or [r, g, b, a] list format.

    Supports:
    - [r, g, b] or (r, g, b) - RGB values 0-255
    - [r, g, b, a] or (r, g, b, a) - RGBA values, alpha 0-255
    - '#RRGGBB' - Hex color string
    - '#RRGGBBAA' - Hex color string with alpha
    - '#RGB' - Short hex format
    - '#RGBA' - Short hex format with alpha
    """
    if isinstance(color, str):
        return _parse_hex_color(color)
    if isinstance(color, (list, tuple)):
        if len(color) not in (3, 4):
            raise ValueError(f"Color must have 3 or 4 components, got {len(color)}")
        return list(color)
    raise TypeError(f"Color must be a list, tuple, or hex string, got {type(color).__name__}")


def _parse_hex_color(hex_str: str) -> List[int]:
    """Parse hex color string to [r, g, b] or [r, g, b, a] list."""
    hex_str = hex_str.strip()
    if not hex_str.startswith('#'):
        raise ValueError(f"Hex color must start with '#', got '{hex_str}'")
    hex_str = hex_str[1:]
    if len(hex_str) == 3:  # #RGB -> #RRGGBB
        hex_str = ''.join(c * 2 for c in hex_str)
    elif len(hex_str) == 4:  # #RGBA -> #RRGGBBAA
        hex_str = ''.join(c * 2 for c in hex_str)
    if len(hex_str) == 6:
        return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]
    elif len(hex_str) == 8:
        return [int(hex_str[i:i+2], 16) for i in (0, 2, 4, 6)]
    raise ValueError(f"Invalid hex color format: '#{hex_str}'")


def is_accessor_string(value: Any) -> bool:
    """Check if value is a deck.gl accessor string (@@=...)."""
    return isinstance(value, str) and value.startswith('@@=')


def is_scale_accessor(value: Any) -> bool:
    """Check if value is a color scale accessor string (@@scale(...))."""
    return isinstance(value, str) and value.startswith('@@scale(')


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase. Handles 'get_' prefix specially."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class BaseLayer(ABC):
    """Abstract base class for all deck.gl layer helpers.

    Provides:
    - Automatic snake_case to camelCase conversion for deck.gl props
    - Color normalization (hex strings, RGB tuples)
    - Accessor string support (@@=property.path)
    - to_dict() serialization for Dash component
    """
    # Override in subclass with the deck.gl layer type name
    _layer_type: str = ''
    # Properties that should have color normalization applied
    _color_props: Tuple[str, ...] = ()
    # Properties that can accept accessor strings (@@=...)
    _accessor_props: Tuple[str, ...] = ()

    def __init__(self, id: str, **kwargs):
        """Initialize layer with id and properties.

        Args:
            id: Unique identifier for the layer
            **kwargs: Layer-specific properties in snake_case
        """
        self._id = id
        self._props: Dict[str, Any] = {}
        for key, value in kwargs.items():
            self._set_prop(key, value)

    @property
    def id(self) -> str:
        """Layer identifier."""
        return self._id

    def _set_prop(self, key: str, value: Any) -> None:
        """Set a property, applying color normalization if needed."""
        if value is None:
            return
        camel_key = to_camel_case(key)
        # Check if this is a color property and not an accessor string or scale accessor
        if key in self._color_props and not is_accessor_string(value) and not is_scale_accessor(value):
            value = normalize_color(value)
        self._props[camel_key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert layer to deck.gl JSON configuration dict."""
        result = {'@@type': self._layer_type, 'id': self._id}
        result.update(self._props)
        return result

    def __repr__(self) -> str:
        props_str = ', '.join(f"{k}={v!r}" for k, v in list(self._props.items())[:3])
        if len(self._props) > 3:
            props_str += ', ...'
        return f"{self.__class__.__name__}(id={self._id!r}, {props_str})"


def process_layers(layers: Optional[Sequence[Union[BaseLayer, Dict[str, Any]]]]) -> Optional[List[Dict[str, Any]]]:
    """Convert a list of layers to dict format for the DeckGL component.

    Accepts:
    - BaseLayer instances (converted via to_dict())
    - Dict objects (passed through unchanged)
    - Mixed lists of both
    """
    if layers is None:
        return None
    result = []
    for layer in layers:
        if isinstance(layer, BaseLayer):
            result.append(layer.to_dict())
        elif isinstance(layer, dict):
            result.append(layer)
        else:
            raise TypeError(f"Layer must be a BaseLayer or dict, got {type(layer).__name__}")
    return result
