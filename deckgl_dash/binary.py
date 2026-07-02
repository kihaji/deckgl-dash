"""Binary data transport for deck.gl layers (issue #39 / T-20).

Packs numpy arrays into one aligned buffer that the JS side rebuilds into deck.gl's
native ``{length, attributes, startIndices}`` binary format — bypassing client-side
JSON tokenization, the real bottleneck for 1M+ item layers. Ported from
deckgl-marimo's ``_binary.py``; Dash lacks a sidecar binary channel, so the buffer
travels as base64-in-JSON (~33% size overhead, but no JSON tokenization).

Usage (either style)::

    from deckgl_dash.binary import binary_data
    layer = ScatterplotLayer(id = 'pts', data = binary_data(
        length = n,
        attributes = {'getPosition': positions_f32_nx2, 'getFillColor': colors_u8_nx4},
    ), get_radius = 30)

    # or the per-layer flag: data is a dict of numpy arrays keyed by accessor name
    ScatterplotLayer(id = 'pts', use_binary = True,
                     data = {'getPosition': positions, 'getFillColor': colors})

numpy is an optional dependency, imported lazily.
"""
from __future__ import annotations
import base64
from typing import Any, Dict, List, Optional

# numpy dtype string -> (JS TypedArray dtype name, byte alignment)
_DTYPE_INFO = {
    'float32': ('float32', 4),
    'float64': ('float64', 8),
    'uint8': ('uint8', 1),
    'uint16': ('uint16', 2),
    'uint32': ('uint32', 4),
    'int32': ('int32', 4),
}


def pack_binary(n: int, attributes: Dict[str, tuple], start_indices: Any = None) -> tuple:
    """Pack attribute arrays into one aligned buffer.

    Args:
        n: Number of data items (rows/features).
        attributes: Mapping of accessor name to (array, dtype, size) — array is
            raveled, dtype is a numpy dtype string, size is components per element.
        start_indices: Optional uint32 array for variable-length geometry (paths/polygons).

    Returns:
        (metadata, buffer) — metadata carries {offset, byteLength, dtype, size} per
        attribute, matching the JS rebuild in layerRegistry.js.
    """
    import numpy as np

    offset = 0
    buffers: List[bytes] = []
    meta_attrs: Dict[str, dict] = {}

    def _append(data_bytes: bytes, alignment: int) -> int:
        nonlocal offset
        if alignment > 1:
            aligned = (offset + alignment - 1) & ~(alignment - 1)
            if aligned > offset:
                buffers.append(b'\x00' * (aligned - offset))
                offset = aligned
        buffers.append(data_bytes)
        start = offset
        offset += len(data_bytes)
        return start

    si_meta = None
    if start_indices is not None:
        si = np.asarray(start_indices, dtype = np.uint32)
        si_bytes = si.tobytes()
        si_meta = {'offset': _append(si_bytes, 4), 'byteLength': len(si_bytes), 'dtype': 'uint32'}

    for attr_name, (array, dtype, size) in attributes.items():
        if dtype not in _DTYPE_INFO:
            raise ValueError(f"Unsupported dtype '{dtype}' for '{attr_name}'. Supported: {sorted(_DTYPE_INFO)}")
        arr = np.asarray(array, dtype = dtype).ravel()
        js_dtype, align = _DTYPE_INFO[dtype]
        arr_bytes = arr.tobytes()
        meta_attrs[attr_name] = {'offset': _append(arr_bytes, align), 'byteLength': len(arr_bytes), 'dtype': js_dtype, 'size': size}

    metadata: Dict[str, Any] = {'length': n, 'attributes': meta_attrs}
    if si_meta is not None:
        metadata['startIndices'] = si_meta
    return metadata, b''.join(buffers)


def _infer_attr_spec(name: str, array: Any) -> tuple:
    """Infer (array, dtype, size) from a numpy array's dtype and shape."""
    import numpy as np

    arr = np.asarray(array)
    size = int(arr.shape[1]) if arr.ndim == 2 else 1
    dtype = str(arr.dtype)
    if dtype == 'float64' or dtype not in _DTYPE_INFO:
        # deck.gl attributes expect float32; halve the payload and match GPU precision.
        # Pass an explicit (array, 'float64', size) tuple to opt out.
        dtype = 'float32' if arr.dtype.kind == 'f' else ('uint32' if arr.dtype.kind == 'u' else 'int32')
    return arr, dtype, size


def binary_data(length: int, attributes: Dict[str, Any], start_indices: Any = None,
                tooltips: Optional[List[str]] = None) -> Dict[str, Any]:
    """Build the JSON-safe ``{'@@binary': ...}`` data block for a layer's ``data`` prop.

    Args:
        length: Number of data items.
        attributes: Accessor name -> numpy array. dtype/size are inferred from the
            array (2D arrays: size = columns), or pass an explicit (array, dtype, size) tuple.
        start_indices: Optional uint32 start offsets for variable-length geometry.
        tooltips: Optional pre-rendered tooltip strings, one per item (binary layers
            carry no ``object`` for tooltip templating, so render them Python-side).
    """
    specs = {}
    for name, value in attributes.items():
        specs[name] = value if isinstance(value, tuple) else _infer_attr_spec(name, value)
    metadata, buffer = pack_binary(length, specs, start_indices = start_indices)
    block: Dict[str, Any] = {**metadata, 'buffer': base64.b64encode(buffer).decode('ascii')}
    if tooltips is not None:
        if len(tooltips) != length:
            raise ValueError(f'tooltips must have one entry per item ({length}), got {len(tooltips)}')
        block['tooltips'] = list(tooltips)
    return {'@@binary': block}


def is_binary_data(data: Any) -> bool:
    """True when a layer ``data`` value is a packed binary block."""
    return isinstance(data, dict) and '@@binary' in data
