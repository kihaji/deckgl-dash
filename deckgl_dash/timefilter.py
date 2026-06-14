"""Time-filter helpers for the animated time slider.

These helpers pair with the DeckGL component's ``time_filter`` prop and a layer's
``get_filter_value`` accessor (GPU ``DataFilterExtension``). Filtering and the playback
animation run entirely client-side at 60fps; the component only reports the throttled
``currentTime`` back to Dash.

``compute_time_domain`` finds the [t_min, t_max] extent of a dataset; ``build_time_filter``
assembles the ``time_filter`` prop dict.

Float32 note: ``DataFilterExtension`` uploads filter values as 32-bit floats, so keep your
time values float32-safe (e.g. *seconds/days since the domain start* rather than raw epoch
seconds). Use ``compute_time_domain`` and store ``t`` on the same scale as ``window``.

Example:
    >>> from deckgl_dash import compute_time_domain, build_time_filter
    >>> domain = compute_time_domain(points, "t")
    >>> tf = build_time_filter(domain, window=(domain[1] - domain[0]) * 0.1)
    >>> DeckGL(id="map", layers=[scatter], time_filter=tf)
"""
from __future__ import annotations
from typing import Any, Callable, List, Optional, Sequence, Union

# An accessor is a dict key, a dotted path ("properties.t"), or a callable item -> number.
TimeAccessor = Union[str, Callable[[Any], Any]]


def _resolve_items(data: Any) -> Any:
    """Return the iterable of records, unwrapping a GeoJSON FeatureCollection."""
    if isinstance(data, dict) and "features" in data:
        return data["features"]
    return data


def _make_getter(accessor: TimeAccessor) -> Callable[[Any], Any]:
    """Build an item -> value getter from a key, dotted path, or callable."""
    if callable(accessor):
        return accessor
    if isinstance(accessor, str):
        parts = accessor.split(".")

        def _get(item: Any) -> Any:
            current = item
            for part in parts:
                if current is None:
                    return None
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    current = getattr(current, part, None)
            return current

        return _get
    raise TypeError(f"accessor must be a str or callable, got {type(accessor).__name__}")


def compute_time_domain(data: Any, accessor: TimeAccessor) -> List[float]:
    """Compute [t_min, t_max] over ``data`` using ``accessor``.

    Args:
        data: A list of records (dicts or objects), or a GeoJSON FeatureCollection.
        accessor: A dict key, a dotted path (e.g. ``"properties.t"``), or a callable
            mapping each item to its numeric time value.

    Returns:
        [t_min, t_max] as floats.

    Raises:
        ValueError: if no numeric time values are found.
    """
    getter = _make_getter(accessor)
    t_min: Optional[float] = None
    t_max: Optional[float] = None
    for item in _resolve_items(data):
        value = getter(item)
        if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        v = float(value)
        if t_min is None or v < t_min:
            t_min = v
        if t_max is None or v > t_max:
            t_max = v
    if t_min is None or t_max is None:
        raise ValueError("compute_time_domain: no numeric time values found in data")
    return [t_min, t_max]


def build_time_filter(
    domain: Sequence[float], window: float, *,
    current: Optional[float] = None,
    playing: bool = False,
    speed: Optional[float] = None,
    loop: bool = True,
    soft_edge: Optional[float] = None,
    layer_ids: Optional[Sequence[str]] = None,
    nonce: Optional[int] = None,
) -> dict:
    """Assemble a ``time_filter`` prop dict for the DeckGL component.

    Args:
        domain: [t_min, t_max] full time extent (e.g. from ``compute_time_domain``).
        window: Sliding-window width; visible data is ``[current - window, current]``.
        current: Initial head time. Defaults to ``domain[0] + window`` (first full window).
        playing: Start the animation immediately.
        speed: Time units advanced per wall-clock second. Defaults to a full sweep in ~20s.
        loop: Wrap the head back to ``domain[0] + window`` at the end.
        soft_edge: Optional fade width mapped to ``filterSoftRange`` for fade in/out.
        layer_ids: Explicit target layer IDs. Defaults to auto-detecting any layer with a
            DataFilterExtension (i.e. any layer given ``get_filter_value``).
        nonce: Bump to force the component to re-sync an unchanged ``current``.

    Returns:
        A dict suitable for ``DeckGL(time_filter=...)``. Keys with ``None`` values are omitted.
    """
    t_min, t_max = float(domain[0]), float(domain[1])
    result = {
        "domain": [t_min, t_max],
        "window": window,
        "current": current if current is not None else t_min + window,
        "playing": playing,
        "speed": speed if speed is not None else (t_max - t_min) / 20.0,
        "loop": loop,
        "softEdge": soft_edge,
        "layerIds": list(layer_ids) if layer_ids is not None else None,
        "nonce": nonce,
    }
    return {k: v for k, v in result.items() if v is not None}
