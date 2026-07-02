import { describe, it, expect } from 'vitest';
import { DataFilterExtension } from '@deck.gl/extensions';
import { computeFilterRange, isFilterTarget, applyRangeToLayers, resolveHeadTime } from '../timeFilter';

describe('computeFilterRange', () => {
    it('builds [T-window, T] hard range', () => {
        expect(computeFilterRange(100, { window: 30 })).toEqual({ range: [70, 100], soft: null });
    });

    it('treats missing window as zero', () => {
        expect(computeFilterRange(50, {})).toEqual({ range: [50, 50], soft: null });
    });

    it('adds a soft fade range when softEdge > 0', () => {
        const { range, soft } = computeFilterRange(100, { window: 30, softEdge: 5 });
        expect(range).toEqual([70, 100]);
        expect(soft).toEqual([65, 105]);
    });

    it('ignores non-positive or non-numeric softEdge', () => {
        expect(computeFilterRange(10, { window: 2, softEdge: 0 }).soft).toBeNull();
        expect(computeFilterRange(10, { window: 2, softEdge: 'big' }).soft).toBeNull();
    });
});

describe('isFilterTarget', () => {
    const filtered = { id: 'a', props: { extensions: [new DataFilterExtension({ filterSize: 1 })] } };
    const plain = { id: 'b', props: { extensions: [] } };

    it('auto-detects layers carrying a DataFilterExtension', () => {
        expect(isFilterTarget(filtered, {})).toBe(true);
        expect(isFilterTarget(plain, {})).toBe(false);
        expect(isFilterTarget(null, {})).toBe(false);
    });

    it('honors an explicit layerIds allowlist over auto-detection', () => {
        expect(isFilterTarget(plain, { layerIds: ['b'] })).toBe(true);
        expect(isFilterTarget(filtered, { layerIds: ['b'] })).toBe(false);
    });
});

describe('applyRangeToLayers', () => {
    const makeLayer = (id, extensions) => ({
        id,
        props: { extensions },
        clone(overrides) { return { ...this, cloned: overrides }; },
    });

    it('clones only filter-target layers with the window range', () => {
        const target = makeLayer('t', [new DataFilterExtension({ filterSize: 1 })]);
        const bystander = makeLayer('b', []);
        const out = applyRangeToLayers([target, bystander], 100, { window: 10 });
        expect(out[0].cloned).toEqual({ filterRange: [90, 100] });
        expect(out[1]).toBe(bystander);
    });

    it('includes filterSoftRange when softEdge is set', () => {
        const target = makeLayer('t', [new DataFilterExtension({ filterSize: 1 })]);
        const out = applyRangeToLayers([target], 100, { window: 10, softEdge: 2 });
        expect(out[0].cloned).toEqual({ filterRange: [90, 100], filterSoftRange: [88, 102] });
    });

    it('passes through when tf or layers are missing', () => {
        const layers = [makeLayer('t', [])];
        expect(applyRangeToLayers(layers, 1, null)).toBe(layers);
        expect(applyRangeToLayers('nope', 1, { window: 1 })).toBe('nope');
    });
});

describe('resolveHeadTime', () => {
    it('prefers tf.current when paused', () => {
        expect(resolveHeadTime({ playing: false, current: 42 }, 7)).toBe(42);
    });

    it('prefers the live ref while playing', () => {
        expect(resolveHeadTime({ playing: true, current: 42 }, 7)).toBe(7);
    });

    it('falls back to current, then domain start + window, then 0', () => {
        expect(resolveHeadTime({ playing: true, current: 42 }, null)).toBe(42);
        expect(resolveHeadTime({ playing: true, domain: [10, 90], window: 5 }, null)).toBe(15);
        expect(resolveHeadTime(null, null)).toBe(0);
    });
});
