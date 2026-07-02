import { describe, it, expect } from 'vitest';
import { extractZoomGates, zoomGateKey, applyZoomVisibility } from '../zoomVisibility';

const CONFIGS = [
    { '@@type': 'TileLayer', id: 'base', minZoom: 0, maxZoom: 19 },
    { '@@type': 'ScatterplotLayer', id: 'pts', visibleMinZoom: 10 },
    { '@@type': 'GeoJsonLayer', id: 'areas', visibleMaxZoom: 9, visible: false },
];

describe('extractZoomGates', () => {
    it('strips gating keys and returns gate descriptors', () => {
        const { configs, gates } = extractZoomGates(CONFIGS);
        expect(configs[1].visibleMinZoom).toBeUndefined();
        expect(configs[2].visibleMaxZoom).toBeUndefined();
        expect(gates).toEqual([
            { id: 'pts', min: 10, max: null, baseVisible: true },
            { id: 'areas', min: null, max: 9, baseVisible: false },
        ]);
    });

    it('leaves TileLayer data-range minZoom/maxZoom alone', () => {
        const { configs } = extractZoomGates(CONFIGS);
        expect(configs[0].minZoom).toBe(0);
        expect(configs[0].maxZoom).toBe(19);
    });

    it('returns the same array when nothing is gated (referential stability)', () => {
        const plain = [{ id: 'a' }, { id: 'b' }];
        const { configs, gates } = extractZoomGates(plain);
        expect(configs).toBe(plain);
        expect(gates).toEqual([]);
    });
});

describe('zoomGateKey', () => {
    const { gates } = extractZoomGates(CONFIGS);

    it('flips exactly at the thresholds', () => {
        expect(zoomGateKey(gates, 9)).toBe('pts:0|areas:1');
        expect(zoomGateKey(gates, 10)).toBe('pts:1|areas:0');
    });

    it('is stable within a band (no churn between thresholds)', () => {
        expect(zoomGateKey(gates, 10.3)).toBe(zoomGateKey(gates, 15));
        expect(zoomGateKey(gates, 2)).toBe(zoomGateKey(gates, 8.9));
    });

    it('is empty with no gates', () => {
        expect(zoomGateKey([], 5)).toBe('');
    });
});

describe('applyZoomVisibility', () => {
    const { gates } = extractZoomGates(CONFIGS);
    const makeLayer = (id) => ({ id, clone(over) { return { ...this, ...over, cloned: true }; } });
    const layers = [makeLayer('base'), makeLayer('pts'), makeLayer('areas')];

    it('folds zoom into visible, respecting the user base visibility', () => {
        const out = applyZoomVisibility(layers, gates, 12);
        expect(out[1].visible).toBe(true);    // pts: min 10, zoom 12
        expect(out[2].visible).toBe(false);   // areas: in-range would be false anyway, and baseVisible false
        const low = applyZoomVisibility(layers, gates, 5);
        expect(low[1].visible).toBe(false);
        expect(low[2].visible).toBe(false);   // baseVisible false wins even in range
    });

    it('passes non-gated layers through untouched', () => {
        const out = applyZoomVisibility(layers, gates, 12);
        expect(out[0]).toBe(layers[0]);
        expect(out[0].cloned).toBeUndefined();
    });

    it('is a no-op without gates', () => {
        expect(applyZoomVisibility(layers, [], 12)).toBe(layers);
    });
});
