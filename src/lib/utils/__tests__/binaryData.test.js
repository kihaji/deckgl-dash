import { describe, it, expect } from 'vitest';
import { createLayer, getBinaryTooltips } from '../layerRegistry';

// Matches deckgl_dash/binary.py: float32 positions at offset 0, uint8 colors after
function makeBinaryBlock() {
    const positions = new Float32Array([0, 0, 1, 1, 2, 2]);       // 3 points, size 2
    const colors = new Uint8Array([255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255]);
    const buf = new Uint8Array(positions.byteLength + colors.byteLength);
    buf.set(new Uint8Array(positions.buffer), 0);
    buf.set(colors, positions.byteLength);
    let b64 = '';
    for (const byte of buf) {
        b64 += String.fromCharCode(byte);
    }
    return {
        length: 3,
        buffer: btoa(b64),
        attributes: {
            getPosition: { offset: 0, byteLength: positions.byteLength, dtype: 'float32', size: 2 },
            getFillColor: { offset: positions.byteLength, byteLength: colors.byteLength, dtype: 'uint8', size: 4 },
        },
        tooltips: ['a', 'b', 'c'],
    };
}

describe('binary data transport', () => {
    it('rebuilds typed arrays into deck.gl native binary format', () => {
        const layer = createLayer({
            '@@type': 'ScatterplotLayer', id: 'bin', data: { '@@binary': makeBinaryBlock() },
        });
        expect(layer).toBeTruthy();
        const data = layer.props.data;
        expect(data.length).toBe(3);
        expect(data.attributes.getPosition.value).toBeInstanceOf(Float32Array);
        expect(Array.from(data.attributes.getPosition.value)).toEqual([0, 0, 1, 1, 2, 2]);
        expect(data.attributes.getFillColor.value).toBeInstanceOf(Uint8Array);
        expect(data.attributes.getFillColor.size).toBe(4);
    });

    it('registers pre-rendered tooltips by layer id', () => {
        createLayer({ '@@type': 'ScatterplotLayer', id: 'bin-tips', data: { '@@binary': makeBinaryBlock() } });
        expect(getBinaryTooltips('bin-tips')).toEqual(['a', 'b', 'c']);
        expect(getBinaryTooltips('nope')).toBeNull();
    });

    it('re-types composite PolygonLayer to SolidPolygonLayer for binary data', () => {
        const positions = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
        let b64 = '';
        for (const byte of new Uint8Array(positions.buffer)) {
            b64 += String.fromCharCode(byte);
        }
        const layer = createLayer({
            '@@type': 'PolygonLayer', id: 'poly', data: { '@@binary': {
                length: 1, buffer: btoa(b64),
                attributes: { getPolygon: { offset: 0, byteLength: positions.byteLength, dtype: 'float32', size: 2 } },
                startIndices: null,
            } },
        });
        expect(layer.constructor.layerName).toBe('SolidPolygonLayer');
    });

    it('leaves plain JSON data untouched', () => {
        const layer = createLayer({ '@@type': 'ScatterplotLayer', id: 'json', data: [{ pos: [0, 0] }] });
        expect(Array.isArray(layer.props.data)).toBe(true);
    });
});
