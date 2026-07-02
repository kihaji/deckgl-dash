"""Shared helpers for the example apps — data generators and basemap shortcuts.

Not part of the deckgl_dash package; import from sibling examples only:
    from _common import osm_tile_layer, TRACK, speeds_to_colors
"""
import math


def osm_tile_layer(layer_id = 'basemap'):
    """The zero-config OSM raster basemap used across the demos (dict/JSON form)."""
    return {
        '@@type': 'TileLayer',
        'id': layer_id,
        'data': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        'minZoom': 0,
        'maxZoom': 19,
        'tileSize': 256,
    }


# An ordered GPS track of (lon, lat, t_seconds) fixes winding through San Francisco.
# The hop from index 6 -> 7 is an "impossible" jump (too far for the elapsed time),
# so speed-based coloring flags exactly one segment.
TRACK = [
    (-122.470, 37.760, 0),
    (-122.455, 37.762, 120),
    (-122.440, 37.765, 240),
    (-122.425, 37.768, 360),
    (-122.410, 37.772, 480),
    (-122.400, 37.776, 600),
    (-122.392, 37.781, 720),
    (-122.360, 37.795, 735),   # <-- impossible: ~3 km in 15 s
    (-122.352, 37.800, 855),
    (-122.345, 37.806, 975),
    (-122.340, 37.812, 1095),
]

IMPOSSIBLE_SPEED_MPS = 100.0      # ~360 km/h
NORMAL_COLOR = [30, 110, 230]     # blue
IMPOSSIBLE_COLOR = [230, 30, 30]  # red


def haversine_m(lon1, lat1, lon2, lat2):
    """Great-circle distance between two lon/lat points, in meters."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def speeds_to_colors(track):
    """One [r, g, b] per segment: red where the implied speed is impossible, else blue.

    Returns a list of length len(track) - 1 (one color per segment).
    """
    colors = []
    for (lon1, lat1, t1), (lon2, lat2, t2) in zip(track, track[1:]):
        dt = max(t2 - t1, 1e-6)
        speed = haversine_m(lon1, lat1, lon2, lat2) / dt
        colors.append(IMPOSSIBLE_COLOR if speed > IMPOSSIBLE_SPEED_MPS else NORMAL_COLOR)
    return colors
