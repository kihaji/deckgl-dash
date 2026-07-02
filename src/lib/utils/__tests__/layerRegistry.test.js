import { describe, it, expect } from 'vitest';
import { parseAccessor, getLayerClass, isLayerRegistered, getRegisteredLayerTypes } from '../layerRegistry';

describe('parseAccessor', () => {
    it('passes through non-strings and plain strings', () => {
        expect(parseAccessor(5)).toBe(5);
        expect(parseAccessor([1, 2, 3])).toEqual([1, 2, 3]);
        expect(parseAccessor('plain')).toBe('plain');
        expect(parseAccessor(null)).toBeNull();
    });

    it('preserves @@scale strings for later data-context resolution', () => {
        const scale = '@@scale(viridis, properties.count)';
        expect(parseAccessor(scale)).toBe(scale);
    });

    it('builds a property-path accessor for simple @@= paths', () => {
        const fn = parseAccessor('@@=properties.name');
        expect(typeof fn).toBe('function');
        expect(fn({ properties: { name: 'x' } })).toBe('x');
        expect(fn({})).toBeUndefined();
    });

    it('supports bracket notation in paths', () => {
        const fn = parseAccessor('@@=coordinates[1]');
        expect(fn({ coordinates: [10, 20] })).toBe(20);
    });

    it('evaluates complex expressions via the Function path', () => {
        const fn = parseAccessor('@@=properties.count > 50 ? [255,0,0] : [0,0,255]');
        expect(typeof fn).toBe('function');
        expect(fn({ properties: { count: 99 } })).toEqual([255, 0, 0]);
        expect(fn({ properties: { count: 1 } })).toEqual([0, 0, 255]);
    });

    it('returns undefined (not a crash) when an expression references missing data', () => {
        const fn = parseAccessor('@@=properties.a.b.c > 1');
        expect(fn({})).toBeUndefined();
    });

    it('handles arithmetic expressions', () => {
        const fn = parseAccessor('@@=properties.value * 2 + 1');
        expect(fn({ properties: { value: 10 } })).toBe(21);
    });
});

describe('layer registry lookups', () => {
    it('resolves registered deck.gl layer types', () => {
        expect(isLayerRegistered('ScatterplotLayer')).toBe(true);
        expect(getLayerClass('ScatterplotLayer')).toBeTruthy();
    });

    it('rejects unknown types', () => {
        expect(isLayerRegistered('NotALayer')).toBe(false);
    });

    it('lists the registered catalog including custom layers', () => {
        const types = getRegisteredLayerTypes();
        expect(types).toContain('GeoJsonLayer');
        expect(types).toContain('MultiColorPathLayer');
        expect(types).toContain('DirectedPathLayer');
    });
});
