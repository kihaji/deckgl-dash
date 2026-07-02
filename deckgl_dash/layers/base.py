"""Base layer class for dash-deckgl Python layer helpers."""
from __future__ import annotations
import difflib
import inspect
from abc import ABC
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple, Union

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
    """Convert snake_case to camelCase, preserving leading underscores (deck.gl experimental props like `_pathType`)."""
    stripped = snake_str.lstrip('_')
    prefix = snake_str[:len(snake_str) - len(stripped)]
    components = stripped.split('_')
    return prefix + components[0] + ''.join(x.title() for x in components[1:])



def _collect_kwargs(cls: type) -> frozenset:
    """Union all keyword parameter names declared by __init__ across cls's MRO.

    Variadic *args/**kwargs and self are skipped. Runs at class-creation time via
    __init_subclass__, so it captures the full typed signature of each layer.
    """
    valid: set = set()
    for klass in cls.__mro__:
        if klass is object:
            continue
        init = klass.__dict__.get('__init__')
        if init is None:
            continue
        try:
            sig = inspect.signature(init)
        except (ValueError, TypeError):
            continue
        for name, param in sig.parameters.items():
            if name == 'self' or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            valid.add(name)
    return frozenset(valid)


# deck.gl base-Layer props valid on every layer; accepted via **kwargs without per-class declarations
_UNIVERSAL_PROPS = frozenset({
    'extensions', 'update_triggers', 'load_options', 'transitions',
    # GPU time filtering works on any layer via DataFilterExtension
    'get_filter_value', 'filter_range', 'filter_soft_range', 'filter_enabled',
    # Zoom-gated visibility (#38) applies to any layer
    'visible_min_zoom', 'visible_max_zoom',
})


def _raise_for_unknown_props(cls_name: str, props: Dict[str, Any], valid: frozenset) -> None:
    """Raise TypeError listing unknown keys with difflib "did you mean" suggestions."""
    unknown = [k for k in props if k not in valid and k not in _UNIVERSAL_PROPS]
    if not unknown:
        return
    valid_sorted = sorted(valid)
    lines = []
    for key in unknown:
        matches = difflib.get_close_matches(key, valid_sorted, n = 3, cutoff = 0.6)
        if matches:
            hint = ', '.join(repr(m) for m in matches)
            lines.append(f"  '{key}' — did you mean: {hint}?")
        else:
            lines.append(f"  '{key}'")
    raise TypeError(
        f"Unknown property/properties for {cls_name}:\n" + '\n'.join(lines) +
        '\n(Pass _unsafe_props=True to bypass this check, e.g. for deck.gl props this wrapper does not declare yet.)'
    )


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
    # Union of declared kwargs across the class and its ancestors; None on BaseLayer
    # itself (no validation for direct/dict-style use). Set by __init_subclass__.
    _VALID_PROPS: ClassVar[Optional[frozenset]] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._VALID_PROPS = _collect_kwargs(cls)

    def __init__(self, id: str, _unsafe_props: bool = False, **kwargs):
        """Initialize layer with id and properties.

        Args:
            id: Unique identifier for the layer
            _unsafe_props: Skip unknown-prop validation (escape hatch for deck.gl
                props this wrapper does not declare yet)
            **kwargs: Layer-specific properties in snake_case
        """
        if not _unsafe_props and self._VALID_PROPS is not None:
            _raise_for_unknown_props(type(self).__name__, kwargs, self._VALID_PROPS)
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
        """Convert layer to deck.gl JSON configuration dict.

        When a `get_filter_value` accessor is present (for GPU time filtering via the
        time slider) and no explicit `extensions` were supplied, the DataFilterExtension
        is auto-attached so `filterRange` updates take effect on the GPU.
        """
        result: Dict[str, Any] = {'@@type': self._layer_type, 'id': self._id}
        result.update(self._props)
        if 'getFilterValue' in result and 'extensions' not in result:
            result['extensions'] = ['DataFilterExtension']
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
