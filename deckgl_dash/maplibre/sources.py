"""MapLibre source classes for deckgl-dash."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


class RasterSource:
    """MapLibre raster tile source.

    Used for XYZ tile servers, WMS, WMTS, or any raster tile endpoint.

    Example - XYZ tiles:
        >>> source = RasterSource(tiles=['https://tile.openstreetmap.org/{z}/{x}/{y}.png'])

    Example - WMS:
        >>> source = RasterSource.from_wms(
        ...     base_url='https://ows.terrestris.de/osm/service',
        ...     layers='TOPO-WMS',
        ...     tile_size=256,
        ... )
    """

    def __init__(
        self,
        tiles: Optional[List[str]] = None,
        tile_size: int = 256,
        min_zoom: int = 0,
        max_zoom: int = 22,
        bounds: Optional[List[float]] = None,
        attribution: Optional[str] = None,
        scheme: str = 'xyz',
    ):
        """Initialize raster source.

        Args:
            tiles: List of tile URL templates with {z}, {x}, {y} placeholders.
            tile_size: Tile size in pixels. Default 256.
            min_zoom: Minimum zoom level. Default 0.
            max_zoom: Maximum zoom level. Default 22.
            bounds: Bounding box [west, south, east, north] in WGS84.
            attribution: Attribution string for the source.
            scheme: Tile scheme - 'xyz' (default) or 'tms'.
        """
        self.tiles = tiles or []
        self.tile_size = tile_size
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.bounds = bounds
        self.attribution = attribution
        self.scheme = scheme

    @classmethod
    def from_wms(
        cls,
        base_url: str,
        layers: str,
        tile_size: int = 256,
        format: str = 'image/png',
        transparent: bool = True,
        version: str = '1.1.1',
        crs: str = 'EPSG:3857',
        styles: str = '',
        extra_params: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> 'RasterSource':
        """Create a raster source from a WMS endpoint.

        Args:
            base_url: WMS service base URL (without query parameters).
            layers: WMS layer name(s) to request. Multiple layers can be comma-separated.
            tile_size: Tile size in pixels. Default 256.
            format: Image format. Default 'image/png'.
            transparent: Request transparent background. Default True.
            version: WMS version. Default '1.1.1'.
            crs: Coordinate reference system. Default 'EPSG:3857' (Web Mercator).
            styles: WMS styles parameter. Default empty string.
            extra_params: Additional WMS parameters to include.
            **kwargs: Additional arguments passed to RasterSource constructor.

        Returns:
            RasterSource configured for the WMS endpoint.
        """
        # Build WMS GetMap URL template
        params = {
            'SERVICE': 'WMS',
            'VERSION': version,
            'REQUEST': 'GetMap',
            'LAYERS': layers,
            'STYLES': styles,
            'FORMAT': format,
            'TRANSPARENT': 'TRUE' if transparent else 'FALSE',
            'WIDTH': str(tile_size),
            'HEIGHT': str(tile_size),
        }

        # Handle CRS/SRS parameter name based on version
        if version.startswith('1.3'):
            params['CRS'] = crs
            params['BBOX'] = '{bbox-epsg-3857}'
        else:
            params['SRS'] = crs
            params['BBOX'] = '{bbox-epsg-3857}'

        # Add extra parameters
        if extra_params:
            params.update(extra_params)

        # Build the full URL
        parsed = urlparse(base_url)
        existing_params = parse_qs(parsed.query)
        # Merge existing query params (single values)
        for k, v in existing_params.items():
            if k.upper() not in params:
                params[k.upper()] = v[0] if v else ''

        query_string = urlencode(params)
        wms_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', query_string, ''))

        return cls(tiles=[wms_url], tile_size=tile_size, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MapLibre source spec dict."""
        result: Dict[str, Any] = {'type': 'raster', 'tiles': self.tiles, 'tileSize': self.tile_size}
        if self.min_zoom != 0:
            result['minzoom'] = self.min_zoom
        if self.max_zoom != 22:
            result['maxzoom'] = self.max_zoom
        if self.bounds:
            result['bounds'] = self.bounds
        if self.attribution:
            result['attribution'] = self.attribution
        if self.scheme != 'xyz':
            result['scheme'] = self.scheme
        return result

    def __repr__(self) -> str:
        return f"RasterSource(tiles={self.tiles}, tile_size={self.tile_size})"


class VectorSource:
    """MapLibre vector tile source for PBF/MVT tiles.

    Example - PBF tiles:
        >>> source = VectorSource(tiles=['https://example.com/{z}/{x}/{y}.pbf'])

    Example - TileJSON:
        >>> source = VectorSource(url='https://example.com/tiles.json')
    """

    def __init__(
        self,
        tiles: Optional[List[str]] = None,
        url: Optional[str] = None,
        min_zoom: int = 0,
        max_zoom: int = 22,
        bounds: Optional[List[float]] = None,
        attribution: Optional[str] = None,
        scheme: str = 'xyz',
        promoteId: Optional[Union[str, Dict[str, str]]] = None,
    ):
        """Initialize vector source.

        Args:
            tiles: List of tile URL templates with {z}, {x}, {y} placeholders.
            url: TileJSON URL (alternative to tiles).
            min_zoom: Minimum zoom level. Default 0.
            max_zoom: Maximum zoom level. Default 22.
            bounds: Bounding box [west, south, east, north] in WGS84.
            attribution: Attribution string for the source.
            scheme: Tile scheme - 'xyz' (default) or 'tms'.
            promoteId: Property to use as feature ID. String for all layers, or dict mapping layer names to properties.
        """
        self.tiles = tiles
        self.url = url
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.bounds = bounds
        self.attribution = attribution
        self.scheme = scheme
        self.promoteId = promoteId

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MapLibre source spec dict."""
        result: Dict[str, Any] = {'type': 'vector'}
        if self.tiles:
            result['tiles'] = self.tiles
        if self.url:
            result['url'] = self.url
        if self.min_zoom != 0:
            result['minzoom'] = self.min_zoom
        if self.max_zoom != 22:
            result['maxzoom'] = self.max_zoom
        if self.bounds:
            result['bounds'] = self.bounds
        if self.attribution:
            result['attribution'] = self.attribution
        if self.scheme != 'xyz':
            result['scheme'] = self.scheme
        if self.promoteId:
            result['promoteId'] = self.promoteId
        return result

    def __repr__(self) -> str:
        if self.url:
            return f"VectorSource(url={self.url!r})"
        return f"VectorSource(tiles={self.tiles})"


class GeoJSONSource:
    """MapLibre GeoJSON source for inline or remote GeoJSON data.

    Example - Inline data:
        >>> source = GeoJSONSource(data={'type': 'FeatureCollection', 'features': [...]})

    Example - Remote URL:
        >>> source = GeoJSONSource(data='https://example.com/data.geojson')
    """

    def __init__(
        self,
        data: Union[str, Dict[str, Any]],
        cluster: bool = False,
        cluster_radius: int = 50,
        cluster_max_zoom: Optional[int] = None,
        cluster_min_points: int = 2,
        cluster_properties: Optional[Dict[str, Any]] = None,
        line_metrics: bool = False,
        tolerance: float = 0.375,
        buffer: int = 128,
        max_zoom: int = 18,
        attribution: Optional[str] = None,
        promoteId: Optional[str] = None,
        generate_id: bool = False,
    ):
        """Initialize GeoJSON source.

        Args:
            data: GeoJSON data (dict) or URL string.
            cluster: Enable point clustering. Default False.
            cluster_radius: Cluster radius in pixels. Default 50.
            cluster_max_zoom: Max zoom to cluster points. Default None (one level below maxzoom).
            cluster_min_points: Minimum points to form a cluster. Default 2.
            cluster_properties: Custom properties for clusters (aggregation expressions).
            line_metrics: Calculate line distance metrics. Default False.
            tolerance: Douglas-Peucker simplification tolerance. Default 0.375.
            buffer: Tile buffer size. Default 128.
            max_zoom: Maximum zoom level to generate tiles. Default 18.
            attribution: Attribution string.
            promoteId: Property to use as feature ID.
            generate_id: Auto-generate feature IDs. Default False.
        """
        self.data = data
        self.cluster = cluster
        self.cluster_radius = cluster_radius
        self.cluster_max_zoom = cluster_max_zoom
        self.cluster_min_points = cluster_min_points
        self.cluster_properties = cluster_properties
        self.line_metrics = line_metrics
        self.tolerance = tolerance
        self.buffer = buffer
        self.max_zoom = max_zoom
        self.attribution = attribution
        self.promoteId = promoteId
        self.generate_id = generate_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MapLibre source spec dict."""
        result: Dict[str, Any] = {'type': 'geojson', 'data': self.data}
        if self.cluster:
            result['cluster'] = True
            result['clusterRadius'] = self.cluster_radius
            if self.cluster_max_zoom is not None:
                result['clusterMaxZoom'] = self.cluster_max_zoom
            if self.cluster_min_points != 2:
                result['clusterMinPoints'] = self.cluster_min_points
            if self.cluster_properties:
                result['clusterProperties'] = self.cluster_properties
        if self.line_metrics:
            result['lineMetrics'] = True
        if self.tolerance != 0.375:
            result['tolerance'] = self.tolerance
        if self.buffer != 128:
            result['buffer'] = self.buffer
        if self.max_zoom != 18:
            result['maxzoom'] = self.max_zoom
        if self.attribution:
            result['attribution'] = self.attribution
        if self.promoteId:
            result['promoteId'] = self.promoteId
        if self.generate_id:
            result['generateId'] = True
        return result

    def __repr__(self) -> str:
        if isinstance(self.data, str):
            return f"GeoJSONSource(data={self.data!r})"
        return f"GeoJSONSource(data=<{len(self.data.get('features', []))} features>)"
