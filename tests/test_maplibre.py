"""Unit tests for deckgl-dash MapLibre helpers."""
import pytest
from deckgl_dash.maplibre import (
    MapLibreConfig, MapLibreStyle,
    RasterSource, VectorSource, GeoJSONSource,
    FillLayer, LineLayer, RasterLayer, CircleLayer, SymbolLayer, FillExtrusionLayer,
)


class TestMapLibreStyle:
    """Tests for MapLibreStyle constants."""

    def test_carto_styles_are_urls(self):
        assert MapLibreStyle.CARTO_POSITRON.startswith('https://')
        assert MapLibreStyle.CARTO_DARK_MATTER.startswith('https://')
        assert MapLibreStyle.CARTO_VOYAGER.startswith('https://')

    def test_openfreemap_styles_are_urls(self):
        assert MapLibreStyle.OPENFREEMAP_LIBERTY.startswith('https://')
        assert MapLibreStyle.OPENFREEMAP_BRIGHT.startswith('https://')
        assert MapLibreStyle.OPENFREEMAP_POSITRON.startswith('https://')

    def test_empty_returns_valid_style(self):
        empty = MapLibreStyle.empty()
        assert empty['version'] == 8
        assert empty['sources'] == {}
        assert empty['layers'] == []


class TestMapLibreConfig:
    """Tests for MapLibreConfig."""

    def test_basic_style_url(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON)
        d = config.to_dict()
        assert d['style'] == MapLibreStyle.CARTO_POSITRON
        assert 'sources' not in d
        assert 'mapLayers' not in d

    def test_inline_style(self):
        style = {'version': 8, 'sources': {}, 'layers': []}
        config = MapLibreConfig(style = style)
        d = config.to_dict()
        assert d['style'] == style

    def test_with_sources_dict(self):
        config = MapLibreConfig(
            style = MapLibreStyle.empty(),
            sources = {'raster': {'type': 'raster', 'tiles': ['https://example.com/{z}/{x}/{y}.png']}},
        )
        d = config.to_dict()
        assert 'raster' in d['sources']
        assert d['sources']['raster']['type'] == 'raster'

    def test_with_source_objects(self):
        config = MapLibreConfig(
            style = MapLibreStyle.empty(),
            sources = {'raster': RasterSource(tiles = ['https://example.com/{z}/{x}/{y}.png'])},
        )
        d = config.to_dict()
        assert d['sources']['raster']['type'] == 'raster'
        assert d['sources']['raster']['tiles'] == ['https://example.com/{z}/{x}/{y}.png']

    def test_with_map_layers_dict(self):
        config = MapLibreConfig(
            style = MapLibreStyle.empty(),
            sources = {'src': {'type': 'raster', 'tiles': []}},
            map_layers = [{'id': 'layer1', 'type': 'raster', 'source': 'src'}],
        )
        d = config.to_dict()
        assert len(d['mapLayers']) == 1
        assert d['mapLayers'][0]['id'] == 'layer1'

    def test_with_layer_objects(self):
        config = MapLibreConfig(
            style = MapLibreStyle.empty(),
            sources = {'src': RasterSource(tiles = ['url'])},
            map_layers = [RasterLayer(id = 'layer1', source = 'src')],
        )
        d = config.to_dict()
        assert d['mapLayers'][0]['type'] == 'raster'
        assert d['mapLayers'][0]['source'] == 'src'

    def test_interleaved_default_false(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON)
        d = config.to_dict()
        assert 'interleaved' not in d  # Only output when True

    def test_interleaved_true(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON, interleaved = True)
        d = config.to_dict()
        assert d['interleaved'] is True

    def test_attribution_control_default_true(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON)
        d = config.to_dict()
        assert 'attributionControl' not in d  # Only output when False

    def test_attribution_control_false(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON, attribution_control = False)
        d = config.to_dict()
        assert d['attributionControl'] is False

    def test_map_options(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON, map_options = {'maxZoom': 18, 'minZoom': 2})
        d = config.to_dict()
        assert d['mapOptions']['maxZoom'] == 18
        assert d['mapOptions']['minZoom'] == 2

    def test_repr(self):
        config = MapLibreConfig(style = MapLibreStyle.CARTO_POSITRON)
        repr_str = repr(config)
        assert 'MapLibreConfig' in repr_str
        assert 'carto' in repr_str.lower()


class TestRasterSource:
    """Tests for RasterSource."""

    def test_basic(self):
        source = RasterSource(tiles = ['https://tile.example.com/{z}/{x}/{y}.png'])
        d = source.to_dict()
        assert d['type'] == 'raster'
        assert d['tiles'] == ['https://tile.example.com/{z}/{x}/{y}.png']
        assert d['tileSize'] == 256

    def test_custom_tile_size(self):
        source = RasterSource(tiles = ['url'], tile_size = 512)
        d = source.to_dict()
        assert d['tileSize'] == 512

    def test_zoom_range(self):
        source = RasterSource(tiles = ['url'], min_zoom = 5, max_zoom = 15)
        d = source.to_dict()
        assert d['minzoom'] == 5
        assert d['maxzoom'] == 15

    def test_bounds(self):
        source = RasterSource(tiles = ['url'], bounds = [-180, -85, 180, 85])
        d = source.to_dict()
        assert d['bounds'] == [-180, -85, 180, 85]

    def test_attribution(self):
        source = RasterSource(tiles = ['url'], attribution = '&copy; OpenStreetMap')
        d = source.to_dict()
        assert d['attribution'] == '&copy; OpenStreetMap'

    def test_scheme_tms(self):
        source = RasterSource(tiles = ['url'], scheme = 'tms')
        d = source.to_dict()
        assert d['scheme'] == 'tms'

    def test_from_wms_basic(self):
        source = RasterSource.from_wms(
            base_url = 'https://ows.example.com/wms',
            layers = 'layer_name',
        )
        d = source.to_dict()
        assert d['type'] == 'raster'
        tiles = d['tiles'][0]
        assert 'SERVICE=WMS' in tiles
        assert 'REQUEST=GetMap' in tiles
        assert 'LAYERS=layer_name' in tiles
        assert 'FORMAT=image%2Fpng' in tiles
        assert 'TRANSPARENT=TRUE' in tiles
        assert 'BBOX=%7Bbbox-epsg-3857%7D' in tiles  # URL encoded {bbox-epsg-3857}

    def test_from_wms_custom_options(self):
        source = RasterSource.from_wms(
            base_url = 'https://example.com/wms',
            layers = 'my_layer',
            tile_size = 512,
            format = 'image/jpeg',
            transparent = False,
            version = '1.3.0',
            crs = 'EPSG:4326',
        )
        d = source.to_dict()
        assert d['tileSize'] == 512
        tiles = d['tiles'][0]
        assert 'FORMAT=image%2Fjpeg' in tiles
        assert 'TRANSPARENT=FALSE' in tiles
        assert 'VERSION=1.3.0' in tiles
        assert 'CRS=EPSG%3A4326' in tiles

    def test_from_wms_extra_params(self):
        source = RasterSource.from_wms(
            base_url = 'https://example.com/wms',
            layers = 'layer',
            extra_params = {'TIME': '2024-01-01', 'CUSTOM': 'value'},
        )
        tiles = source.to_dict()['tiles'][0]
        assert 'TIME=2024-01-01' in tiles
        assert 'CUSTOM=value' in tiles

    def test_repr(self):
        source = RasterSource(tiles = ['url1', 'url2'])
        repr_str = repr(source)
        assert 'RasterSource' in repr_str


class TestVectorSource:
    """Tests for VectorSource."""

    def test_basic_tiles(self):
        source = VectorSource(tiles = ['https://example.com/{z}/{x}/{y}.pbf'])
        d = source.to_dict()
        assert d['type'] == 'vector'
        assert d['tiles'] == ['https://example.com/{z}/{x}/{y}.pbf']

    def test_tilejson_url(self):
        source = VectorSource(url = 'https://example.com/tiles.json')
        d = source.to_dict()
        assert d['type'] == 'vector'
        assert d['url'] == 'https://example.com/tiles.json'

    def test_promote_id_string(self):
        source = VectorSource(tiles = ['url'], promoteId = 'feature_id')
        d = source.to_dict()
        assert d['promoteId'] == 'feature_id'

    def test_promote_id_dict(self):
        source = VectorSource(tiles = ['url'], promoteId = {'layer1': 'id1', 'layer2': 'id2'})
        d = source.to_dict()
        assert d['promoteId'] == {'layer1': 'id1', 'layer2': 'id2'}

    def test_repr_tiles(self):
        source = VectorSource(tiles = ['url'])
        assert 'VectorSource' in repr(source)

    def test_repr_url(self):
        source = VectorSource(url = 'https://example.com/tiles.json')
        assert 'VectorSource' in repr(source)
        assert 'tiles.json' in repr(source)


class TestGeoJSONSource:
    """Tests for GeoJSONSource."""

    def test_inline_data(self):
        data = {'type': 'FeatureCollection', 'features': []}
        source = GeoJSONSource(data = data)
        d = source.to_dict()
        assert d['type'] == 'geojson'
        assert d['data'] == data

    def test_url_data(self):
        source = GeoJSONSource(data = 'https://example.com/data.geojson')
        d = source.to_dict()
        assert d['data'] == 'https://example.com/data.geojson'

    def test_clustering(self):
        source = GeoJSONSource(data = [], cluster = True, cluster_radius = 75, cluster_max_zoom = 14)
        d = source.to_dict()
        assert d['cluster'] is True
        assert d['clusterRadius'] == 75
        assert d['clusterMaxZoom'] == 14

    def test_line_metrics(self):
        source = GeoJSONSource(data = [], line_metrics = True)
        d = source.to_dict()
        assert d['lineMetrics'] is True

    def test_generate_id(self):
        source = GeoJSONSource(data = [], generate_id = True)
        d = source.to_dict()
        assert d['generateId'] is True

    def test_repr_url(self):
        source = GeoJSONSource(data = 'https://example.com/data.geojson')
        assert 'GeoJSONSource' in repr(source)

    def test_repr_inline(self):
        source = GeoJSONSource(data = {'type': 'FeatureCollection', 'features': [1, 2, 3]})
        assert 'GeoJSONSource' in repr(source)
        assert '3 features' in repr(source)


class TestFillLayer:
    """Tests for FillLayer."""

    def test_basic(self):
        layer = FillLayer(id = 'fill', source = 'src', source_layer = 'buildings')
        d = layer.to_dict()
        assert d['type'] == 'fill'
        assert d['id'] == 'fill'
        assert d['source'] == 'src'
        assert d['source-layer'] == 'buildings'

    def test_paint_properties(self):
        layer = FillLayer(
            id = 'fill', source = 'src',
            fill_color = '#ff0000', fill_opacity = 0.5, fill_outline_color = '#000000'
        )
        d = layer.to_dict()
        assert d['paint']['fill-color'] == '#ff0000'
        assert d['paint']['fill-opacity'] == 0.5
        assert d['paint']['fill-outline-color'] == '#000000'

    def test_layout_properties(self):
        layer = FillLayer(id = 'fill', source = 'src', visibility = 'visible')
        d = layer.to_dict()
        assert d['layout']['visibility'] == 'visible'

    def test_filter(self):
        layer = FillLayer(id = 'fill', source = 'src', filter = ['==', ['get', 'type'], 'building'])
        d = layer.to_dict()
        assert d['filter'] == ['==', ['get', 'type'], 'building']

    def test_zoom_range(self):
        layer = FillLayer(id = 'fill', source = 'src', min_zoom = 10, max_zoom = 18)
        d = layer.to_dict()
        assert d['minzoom'] == 10
        assert d['maxzoom'] == 18

    def test_repr(self):
        layer = FillLayer(id = 'fill', source = 'src')
        assert 'FillLayer' in repr(layer)


class TestLineLayer:
    """Tests for LineLayer."""

    def test_basic(self):
        layer = LineLayer(id = 'line', source = 'src', source_layer = 'roads')
        d = layer.to_dict()
        assert d['type'] == 'line'
        assert d['source-layer'] == 'roads'

    def test_paint_properties(self):
        layer = LineLayer(
            id = 'line', source = 'src',
            line_color = '#0000ff', line_width = 2, line_opacity = 0.8, line_dasharray = [2, 1]
        )
        d = layer.to_dict()
        assert d['paint']['line-color'] == '#0000ff'
        assert d['paint']['line-width'] == 2
        assert d['paint']['line-opacity'] == 0.8
        assert d['paint']['line-dasharray'] == [2, 1]

    def test_layout_properties(self):
        layer = LineLayer(id = 'line', source = 'src', line_cap = 'round', line_join = 'round')
        d = layer.to_dict()
        assert d['layout']['line-cap'] == 'round'
        assert d['layout']['line-join'] == 'round'


class TestRasterLayer:
    """Tests for RasterLayer."""

    def test_basic(self):
        layer = RasterLayer(id = 'raster', source = 'src')
        d = layer.to_dict()
        assert d['type'] == 'raster'
        assert d['source'] == 'src'
        assert 'source-layer' not in d  # Raster layers don't use source-layer

    def test_paint_properties(self):
        layer = RasterLayer(
            id = 'raster', source = 'src',
            raster_opacity = 0.8, raster_saturation = -0.5, raster_contrast = 0.2
        )
        d = layer.to_dict()
        assert d['paint']['raster-opacity'] == 0.8
        assert d['paint']['raster-saturation'] == -0.5
        assert d['paint']['raster-contrast'] == 0.2


class TestCircleLayer:
    """Tests for CircleLayer."""

    def test_basic(self):
        layer = CircleLayer(id = 'circle', source = 'src')
        d = layer.to_dict()
        assert d['type'] == 'circle'

    def test_paint_properties(self):
        layer = CircleLayer(
            id = 'circle', source = 'src',
            circle_radius = 6, circle_color = '#007cbf', circle_stroke_width = 2, circle_stroke_color = '#ffffff'
        )
        d = layer.to_dict()
        assert d['paint']['circle-radius'] == 6
        assert d['paint']['circle-color'] == '#007cbf'
        assert d['paint']['circle-stroke-width'] == 2
        assert d['paint']['circle-stroke-color'] == '#ffffff'


class TestSymbolLayer:
    """Tests for SymbolLayer."""

    def test_basic(self):
        layer = SymbolLayer(id = 'symbol', source = 'src')
        d = layer.to_dict()
        assert d['type'] == 'symbol'

    def test_text_layout(self):
        layer = SymbolLayer(
            id = 'labels', source = 'src',
            text_field = ['get', 'name'], text_size = 12, text_font = ['Open Sans Bold']
        )
        d = layer.to_dict()
        assert d['layout']['text-field'] == ['get', 'name']
        assert d['layout']['text-size'] == 12
        assert d['layout']['text-font'] == ['Open Sans Bold']

    def test_text_paint(self):
        layer = SymbolLayer(
            id = 'labels', source = 'src',
            text_color = '#000000', text_halo_color = '#ffffff', text_halo_width = 1
        )
        d = layer.to_dict()
        assert d['paint']['text-color'] == '#000000'
        assert d['paint']['text-halo-color'] == '#ffffff'
        assert d['paint']['text-halo-width'] == 1


class TestFillExtrusionLayer:
    """Tests for FillExtrusionLayer."""

    def test_basic(self):
        layer = FillExtrusionLayer(id = 'extrusion', source = 'src', source_layer = 'buildings')
        d = layer.to_dict()
        assert d['type'] == 'fill-extrusion'
        assert d['source-layer'] == 'buildings'

    def test_paint_properties(self):
        layer = FillExtrusionLayer(
            id = 'extrusion', source = 'src',
            fill_extrusion_color = '#aaa',
            fill_extrusion_height = ['get', 'height'],
            fill_extrusion_base = ['get', 'min_height'],
            fill_extrusion_opacity = 0.6
        )
        d = layer.to_dict()
        assert d['paint']['fill-extrusion-color'] == '#aaa'
        assert d['paint']['fill-extrusion-height'] == ['get', 'height']
        assert d['paint']['fill-extrusion-base'] == ['get', 'min_height']
        assert d['paint']['fill-extrusion-opacity'] == 0.6
