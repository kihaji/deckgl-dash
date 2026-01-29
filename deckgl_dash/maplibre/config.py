"""MapLibre configuration classes for deckgl-dash."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union


class MapLibreStyle:
    """Pre-defined MapLibre style URLs for common basemap providers.

    Example:
        >>> from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle
        >>> config = MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON)
    """
    # CARTO Basemaps (no API key required for light usage)
    CARTO_POSITRON = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
    CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
    CARTO_VOYAGER = 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json'

    # OpenFreeMap (free, no API key required)
    OPENFREEMAP_LIBERTY = 'https://tiles.openfreemap.org/styles/liberty'
    OPENFREEMAP_BRIGHT = 'https://tiles.openfreemap.org/styles/bright'
    OPENFREEMAP_POSITRON = 'https://tiles.openfreemap.org/styles/positron'

    # MapTiler (requires API key appended as ?key=YOUR_KEY)
    MAPTILER_STREETS = 'https://api.maptiler.com/maps/streets/style.json'
    MAPTILER_BASIC = 'https://api.maptiler.com/maps/basic/style.json'
    MAPTILER_SATELLITE = 'https://api.maptiler.com/maps/satellite/style.json'
    MAPTILER_HYBRID = 'https://api.maptiler.com/maps/hybrid/style.json'
    MAPTILER_OUTDOOR = 'https://api.maptiler.com/maps/outdoor/style.json'

    @staticmethod
    def empty() -> Dict[str, Any]:
        """Return an empty style spec for custom/WMS-only maps."""
        return {'version': 8, 'sources': {}, 'layers': []}


class MapLibreConfig:
    """Configuration for MapLibre GL JS integration with deck.gl.

    When maplibre_config is provided to the DeckGL component, MapLibre GL JS
    renders the basemap and deck.gl layers are rendered as overlays via MapboxOverlay.

    Example - Simple basemap:
        >>> from deckgl_dash.maplibre import MapLibreConfig, MapLibreStyle
        >>> config = MapLibreConfig(style=MapLibreStyle.CARTO_POSITRON)
        >>> DeckGL(maplibre_config=config.to_dict(), layers=[...])

    Example - WMS layer:
        >>> from deckgl_dash.maplibre import MapLibreConfig, RasterSource, RasterLayer
        >>> config = MapLibreConfig(
        ...     style=MapLibreStyle.empty(),
        ...     sources={'wms': RasterSource.from_wms('https://example.com/wms', 'layer_name')},
        ...     map_layers=[RasterLayer(id='wms-layer', source='wms')],
        ... )

    Example - Custom PBF vector tiles:
        >>> from deckgl_dash.maplibre import MapLibreConfig, VectorSource, FillLayer
        >>> config = MapLibreConfig(
        ...     style=MapLibreStyle.CARTO_POSITRON,
        ...     sources={'custom': VectorSource(tiles=['https://example.com/{z}/{x}/{y}.pbf'])},
        ...     map_layers=[FillLayer(id='custom-fill', source='custom', source_layer='buildings')],
        ... )
    """

    def __init__(
        self,
        style: Union[str, Dict[str, Any]],
        sources: Optional[Dict[str, Any]] = None,
        map_layers: Optional[List[Any]] = None,
        interleaved: bool = False,
        attribution_control: bool = True,
        map_options: Optional[Dict[str, Any]] = None,
    ):
        """Initialize MapLibre configuration.

        Args:
            style: MapLibre style URL (string) or inline style spec (dict).
                   Use MapLibreStyle constants for common basemaps.
            sources: Additional sources to add to the map. Dict of {source_id: source_spec}.
                     Source specs can be dicts or Source objects (RasterSource, VectorSource, etc.).
            map_layers: Additional MapLibre layers to add to the map. List of layer specs.
                        Layer specs can be dicts or Layer objects (FillLayer, RasterLayer, etc.).
            interleaved: Enable deck.gl layer interleaving with MapLibre layers. Default False
                         for better performance. Set True to render deck.gl layers between
                         MapLibre layers (e.g., below labels) using beforeId.
            attribution_control: Show MapLibre attribution control. Default True.
            map_options: Additional options passed to MapLibre Map constructor.
        """
        self.style = style
        self.sources = sources or {}
        self.map_layers = map_layers or []
        self.interleaved = interleaved
        self.attribution_control = attribution_control
        self.map_options = map_options or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format for the DeckGL component maplibreConfig prop."""
        # Convert source objects to dicts
        sources_dict = {}
        for source_id, source_spec in self.sources.items():
            if hasattr(source_spec, 'to_dict'):
                sources_dict[source_id] = source_spec.to_dict()
            else:
                sources_dict[source_id] = source_spec

        # Convert layer objects to dicts
        layers_list = []
        for layer_spec in self.map_layers:
            if hasattr(layer_spec, 'to_dict'):
                layers_list.append(layer_spec.to_dict())
            else:
                layers_list.append(layer_spec)

        result: Dict[str, Any] = {'style': self.style}
        if sources_dict:
            result['sources'] = sources_dict
        if layers_list:
            result['mapLayers'] = layers_list
        if self.interleaved:
            result['interleaved'] = True
        if not self.attribution_control:
            result['attributionControl'] = False
        if self.map_options:
            result['mapOptions'] = self.map_options
        return result

    def __repr__(self) -> str:
        style_repr = self.style if isinstance(self.style, str) else '<inline style>'
        return f"MapLibreConfig(style={style_repr!r}, sources={len(self.sources)}, map_layers={len(self.map_layers)})"
