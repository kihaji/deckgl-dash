"""Coordinate conversion utilities for deckgl-dash.

Provides a CoordinateConverter class for converting between coordinate formats:
- DD (Decimal Degrees) - the native format from deck.gl click events
- DMS (Degrees Minutes Seconds)
- UTM (Universal Transverse Mercator)
- MGRS (Military Grid Reference System)

Example:
    >>> from deckgl_dash.coordinates import CoordinateConverter
    >>>
    >>> # In a Dash callback:
    >>> @callback(Output('coords-display', 'children'), Input('map', 'clickInfo'))
    >>> def show_coords(click_info):
    ...     if not click_info or not click_info.get('coordinate'):
    ...         return "Click on the map..."
    ...     coord = CoordinateConverter.from_click_info(click_info)
    ...     return f"DD: {coord.dd} | DMS: {coord.dms} | UTM: {coord.utm} | MGRS: {coord.mgrs}"
"""
from __future__ import annotations
import math
from typing import Any, Dict, Tuple


def _dd_to_dms(decimal_degrees: float) -> Tuple[int, int, float]:
    """Convert decimal degrees to (degrees, minutes, seconds)."""
    sign = 1 if decimal_degrees >= 0 else -1
    dd = abs(decimal_degrees)
    degrees = int(dd)
    minutes_full = (dd - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    return (sign * degrees, minutes, seconds)


def _format_dms_lat(decimal_degrees: float, precision: int = 2) -> str:
    """Format latitude as DMS string with N/S hemisphere indicator."""
    hemisphere = "N" if decimal_degrees >= 0 else "S"
    degrees, minutes, seconds = _dd_to_dms(decimal_degrees)
    return f"{abs(degrees)}\u00b0 {minutes}' {seconds:.{precision}f}\" {hemisphere}"


def _format_dms_lon(decimal_degrees: float, precision: int = 2) -> str:
    """Format longitude as DMS string with E/W hemisphere indicator."""
    hemisphere = "E" if decimal_degrees >= 0 else "W"
    degrees, minutes, seconds = _dd_to_dms(decimal_degrees)
    return f"{abs(degrees)}\u00b0 {minutes}' {seconds:.{precision}f}\" {hemisphere}"


class CoordinateConverter:
    """Convert geographic coordinates between DD, DMS, UTM, and MGRS formats.

    Accepts WGS84 longitude/latitude (the native format from deck.gl click events).

    Example:
        >>> coord = CoordinateConverter(-122.4194, 37.7749)
        >>> coord.dd
        '37.774900 N, 122.419400 W'
        >>> coord.dms
        '37° 46\\' 29.64" N, 122° 25\\' 9.84" W'
        >>> coord.utm
        '10S 551234 4182345'
        >>> coord.mgrs
        '10SEG5123482345'
    """

    def __init__(self, longitude: float, latitude: float):
        if not -180 <= longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
        if not -90 <= latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        self._longitude = float(longitude)
        self._latitude = float(latitude)

    @classmethod
    def from_click_info(cls, click_info: Dict[str, Any]) -> CoordinateConverter:
        """Create a CoordinateConverter from a deck.gl clickInfo dict.

        Args:
            click_info: The clickInfo dict from a DeckGL component callback.
                        Must contain a 'coordinate' key with [longitude, latitude].

        Returns:
            CoordinateConverter instance

        Raises:
            ValueError: If click_info is missing or has no coordinate data
        """
        if not click_info or not click_info.get('coordinate'):
            raise ValueError("click_info must contain a 'coordinate' key with [longitude, latitude]")
        coord = click_info['coordinate']
        return cls(longitude = coord[0], latitude = coord[1])

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def dd_tuple(self) -> Tuple[float, float]:
        """Raw (latitude, longitude) as a tuple."""
        return (self._latitude, self._longitude)

    @property
    def dd(self) -> str:
        """Decimal Degrees formatted string (e.g., '37.774900 N, 122.419400 W')."""
        lat_dir = "N" if self._latitude >= 0 else "S"
        lon_dir = "E" if self._longitude >= 0 else "W"
        return f"{abs(self._latitude):.6f} {lat_dir}, {abs(self._longitude):.6f} {lon_dir}"

    @property
    def dms(self) -> str:
        """Degrees Minutes Seconds formatted string."""
        return f"{_format_dms_lat(self._latitude)}, {_format_dms_lon(self._longitude)}"

    def dms_precision(self, precision: int = 2) -> str:
        """DMS with configurable decimal places on seconds.

        Args:
            precision: Number of decimal places for seconds (default 2)
        """
        return f"{_format_dms_lat(self._latitude, precision)}, {_format_dms_lon(self._longitude, precision)}"

    @property
    def utm(self) -> str:
        """Universal Transverse Mercator formatted string (e.g., '10S 551234 4182345').

        Requires pyproj. Install with: pip install pyproj
        """
        try:
            from pyproj import Proj  # type: ignore[import-not-found]
        except ImportError:
            raise ImportError("pyproj is required for UTM conversion. Install with: pip install pyproj") from None

        zone_number = _utm_zone_number(self._longitude, self._latitude)
        zone_letter = _utm_zone_letter(self._latitude)
        proj = Proj(proj = 'utm', zone = zone_number, ellps = 'WGS84', south = self._latitude < 0)
        easting, northing = proj(self._longitude, self._latitude)
        return f"{zone_number}{zone_letter} {int(round(easting))} {int(round(northing))}"

    @property
    def mgrs(self) -> str:
        """Military Grid Reference System string with 5-digit precision (1m accuracy).

        Requires mgrs. Install with: pip install mgrs
        """
        return self.mgrs_precision(5)

    def mgrs_precision(self, precision: int = 5) -> str:
        """MGRS with configurable precision (1-5 digits).

        Args:
            precision: Number of digits for easting/northing (1=10km, 2=1km, 3=100m, 4=10m, 5=1m)

        Requires mgrs. Install with: pip install mgrs
        """
        try:
            import mgrs as mgrs_lib  # type: ignore[import-not-found]
        except ImportError:
            raise ImportError("mgrs is required for MGRS conversion. Install with: pip install mgrs") from None

        if not 1 <= precision <= 5:
            raise ValueError(f"MGRS precision must be 1-5, got {precision}")
        m = mgrs_lib.MGRS()
        return m.toMGRS(self._latitude, self._longitude, MGRSPrecision = precision)

    def as_dict(self, include_utm: bool = False, include_mgrs: bool = False) -> Dict[str, Any]:
        """Return all coordinate formats as a dictionary.

        By default only includes DD and DMS (no external dependencies).
        Set include_utm=True or include_mgrs=True to include those formats
        (requires pyproj and mgrs packages respectively).

        Args:
            include_utm: Include UTM format (requires pyproj)
            include_mgrs: Include MGRS format (requires mgrs)
        """
        result: Dict[str, Any] = {
            'longitude': self._longitude,
            'latitude': self._latitude,
            'dd': self.dd,
            'dd_tuple': self.dd_tuple,
            'dms': self.dms,
        }
        if include_utm:
            result['utm'] = self.utm
        if include_mgrs:
            result['mgrs'] = self.mgrs
        return result

    def __repr__(self) -> str:
        return f"CoordinateConverter(longitude={self._longitude}, latitude={self._latitude})"


def _utm_zone_number(longitude: float, latitude: float) -> int:
    """Calculate UTM zone number from longitude/latitude."""
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        return 32
    if 72 <= latitude <= 84:
        if 0 <= longitude < 9:
            return 31
        elif 9 <= longitude < 21:
            return 33
        elif 21 <= longitude < 33:
            return 35
        elif 33 <= longitude < 42:
            return 37
    return int(math.floor((longitude + 180) / 6)) + 1


def _utm_zone_letter(latitude: float) -> str:
    """Calculate UTM zone letter from latitude."""
    letters = "CDEFGHJKLMNPQRSTUVWX"
    if -80 <= latitude <= 84:
        idx = int((latitude + 80) / 8)
        idx = min(idx, len(letters) - 1)
        return letters[idx]
    return ""
