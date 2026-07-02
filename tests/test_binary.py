"""Tests for the binary data transport (issue #39 / T-20)."""
import base64
import numpy as np
import pytest

from deckgl_dash.binary import pack_binary, binary_data, is_binary_data
from deckgl_dash.layers import ScatterplotLayer, PolygonLayer


class TestPackBinary:
    def test_single_attribute_layout(self):
        positions = np.arange(8, dtype = np.float32).reshape(4, 2)
        meta, buf = pack_binary(4, {'getPosition': (positions, 'float32', 2)})
        assert meta['length'] == 4
        a = meta['attributes']['getPosition']
        assert a == {'offset': 0, 'byteLength': 32, 'dtype': 'float32', 'size': 2}
        assert np.frombuffer(buf, dtype = np.float32).tolist() == list(range(8))

    def test_alignment_padding(self):
        colors = np.zeros((3, 4), dtype = np.uint8)      # 12 bytes
        positions = np.zeros((3, 2), dtype = np.float32)  # needs 4-byte alignment
        meta, buf = pack_binary(3, {'getFillColor': (colors, 'uint8', 4), 'getPosition': (positions, 'float32', 2)})
        pos_meta = meta['attributes']['getPosition']
        assert pos_meta['offset'] % 4 == 0
        assert len(buf) == pos_meta['offset'] + pos_meta['byteLength']

    def test_start_indices(self):
        meta, buf = pack_binary(2, {'getPolygon': (np.zeros(12, dtype = np.float32), 'float32', 2)},
                                start_indices = np.array([0, 3], dtype = np.uint32))
        si = meta['startIndices']
        assert si['dtype'] == 'uint32'
        assert np.frombuffer(buf[si['offset']:si['offset'] + si['byteLength']], dtype = np.uint32).tolist() == [0, 3]

    def test_unsupported_dtype_raises(self):
        with pytest.raises(ValueError, match = 'Unsupported dtype'):
            pack_binary(1, {'x': (np.zeros(1, dtype = np.int64), 'int64', 1)})


class TestBinaryData:
    def test_infers_dtype_and_size(self):
        block = binary_data(4, {'getPosition': np.zeros((4, 2), dtype = np.float32),
                                'getFillColor': np.zeros((4, 4), dtype = np.uint8)})
        assert is_binary_data(block)
        b = block['@@binary']
        assert b['length'] == 4
        assert b['attributes']['getPosition']['size'] == 2
        assert b['attributes']['getFillColor']['dtype'] == 'uint8'
        base64.b64decode(b['buffer'])  # valid base64

    def test_float64_coerced_to_float32(self):
        block = binary_data(2, {'getPosition': np.zeros((2, 2))})  # default float64
        assert block['@@binary']['attributes']['getPosition']['dtype'] == 'float32'

    def test_tooltips_length_checked(self):
        with pytest.raises(ValueError, match = 'tooltips'):
            binary_data(3, {'getPosition': np.zeros((3, 2), dtype = np.float32)}, tooltips = ['only-one'])
        block = binary_data(2, {'getPosition': np.zeros((2, 2), dtype = np.float32)}, tooltips = ['a', 'b'])
        assert block['@@binary']['tooltips'] == ['a', 'b']


class TestUseBinaryFlag:
    def test_layer_packs_data(self):
        layer = ScatterplotLayer(id = 'pts', use_binary = True,
                                 data = {'getPosition': np.zeros((5, 2), dtype = np.float32)},
                                 get_radius = 30)
        d = layer.to_dict()
        assert is_binary_data(d['data'])
        assert d['data']['@@binary']['length'] == 5
        assert d['getRadius'] == 30
        assert 'useBinary' not in d

    def test_prepacked_block_passes_through(self):
        block = binary_data(2, {'getPosition': np.zeros((2, 2), dtype = np.float32)})
        d = ScatterplotLayer(id = 'pts', use_binary = True, data = block).to_dict()
        assert d['data'] is block

    def test_polygon_binary_length_from_start_indices(self):
        d = PolygonLayer(id = 'polys', use_binary = True, data = {
            'getPolygon': np.zeros((10, 2), dtype = np.float32),
            'startIndices': np.array([0, 4], dtype = np.uint32),
        }).to_dict()
        assert d['data']['@@binary']['length'] == 2
        assert 'startIndices' in d['data']['@@binary']

    def test_empty_data_dict_raises(self):
        with pytest.raises(ValueError, match = 'at least one accessor'):
            ScatterplotLayer(id = 'pts', use_binary = True, data = {}).to_dict()
