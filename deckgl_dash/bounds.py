"""Geographic bounds computation for the `fit_bounds` prop.

`compute_bounds` extracts a [[west, south], [east, north]] box from a variety of
inputs — point lists, path/polygon dicts, and GeoJSON (FeatureCollection, Feature,
or geometry) — by recursively collecting [lon, lat] pairs. Pass the result as the
`bounds` of a `fit_bounds` dict on the DeckGL component.

Example:
    >>> from deckgl_dash.bounds import compute_bounds
    >>> compute_bounds([{"coordinates": [-122.4, 37.8]}, {"coordinates": [-122.3, 37.9]}])
    [[-122.4, 37.8], [-122.3, 37.9]]
    >>> DeckGL(id="map", fit_bounds={"bounds": compute_bounds(points), "padding": 40})
"""
from __future__ import annotations
from typing import Any, Callable, List, Optional, Tuple

_Number = (int, float)
# Keys that hold coordinates in common deck.gl data shapes and GeoJSON.
_COORD_KEYS = ("path", "polygon", "position", "contour", "sourcePosition", "targetPosition", "from", "to")


def _is_point(x: Any) -> bool:
    """True if x is a [lon, lat(, ...)] coordinate pair (bool excluded — bool is an int subclass)."""
    return (isinstance(x, (list, tuple)) and len(x) >= 2
            and isinstance(x[0], _Number) and not isinstance(x[0], bool)
            and isinstance(x[1], _Number) and not isinstance(x[1], bool))


def _walk(obj: Any, out: List[Tuple[float, float]]) -> None:
    """Recursively collect [lon, lat] pairs from arbitrary nested coordinate structures."""
    if obj is None:
        return
    if _is_point(obj):
        out.append((float(obj[0]), float(obj[1])))
        return
    if isinstance(obj, (list, tuple)):
        for item in obj:
            _walk(item, out)
        return
    if isinstance(obj, dict):
        if "features" in obj:
            _walk(obj["features"], out)
        if "geometry" in obj:
            _walk(obj["geometry"], out)
        if "coordinates" in obj:
            _walk(obj["coordinates"], out)
        for key in _COORD_KEYS:
            if key in obj:
                _walk(obj[key], out)


def compute_bounds(data: Any, *, get_coordinates: Optional[Callable[[Any], Any]] = None) -> List[List[float]]:
    """Compute [[west, south], [east, north]] enclosing all coordinates in `data`.

    Args:
        data: A GeoJSON dict (FeatureCollection/Feature/geometry), or a list of items
            (each a [lon, lat] pair, a dict with `coordinates`/`path`/`polygon`/`position`,
            or a GeoJSON Feature).
        get_coordinates: Optional accessor mapping each item to its coordinate(s); use
            when coordinates live under a non-standard key.

    Returns:
        [[west, south], [east, north]].

    Raises:
        ValueError: if no coordinates are found.
    """
    points: List[Tuple[float, float]] = []
    if get_coordinates is not None:
        items = data["features"] if isinstance(data, dict) and "features" in data else data
        for item in items:
            _walk(get_coordinates(item), points)
    else:
        _walk(data, points)

    if not points:
        raise ValueError("compute_bounds: no coordinates found in data")

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return [[min(lons), min(lats)], [max(lons), max(lats)]]
