import { describe, it, expect } from 'vitest';
import { isEventEnabled, normalizePickInfo, serializeObject } from '../eventHandler';

describe('isEventEnabled', () => {
    it('returns true for everything when enableEvents is true', () => {
        expect(isEventEnabled('click', true)).toBe(true);
        expect(isEventEnabled('hover', true)).toBe(true);
    });

    it('honors an array allowlist', () => {
        expect(isEventEnabled('click', ['click'])).toBe(true);
        expect(isEventEnabled('hover', ['click'])).toBe(false);
    });

    it('returns false for false/undefined/garbage', () => {
        expect(isEventEnabled('click', false)).toBe(false);
        expect(isEventEnabled('click', undefined)).toBe(false);
        expect(isEventEnabled('click', 'yes')).toBe(false);
    });
});

describe('normalizePickInfo', () => {
    it('returns null for missing info', () => {
        expect(normalizePickInfo(null)).toBeNull();
        expect(normalizePickInfo(undefined)).toBeNull();
    });

    it('normalizes a picked feature', () => {
        const info = {
            picked: true,
            index: 3,
            layer: { id: 'pts' },
            coordinate: [1.5, 2.5],
            x: 10,
            y: 20,
            pixel: [10, 20],
            object: { name: 'a', value: 42 },
        };
        const n = normalizePickInfo(info);
        expect(n.picked).toBe(true);
        expect(n.index).toBe(3);
        expect(n.layerId).toBe('pts');
        expect(n.coordinate).toEqual([1.5, 2.5]);
        expect(n.object).toEqual({ name: 'a', value: 42 });
    });

    it('copies coordinate/pixel arrays rather than aliasing them', () => {
        const info = { picked: true, index: 0, coordinate: [1, 2], pixel: [3, 4], x: 3, y: 4, object: {} };
        const n = normalizePickInfo(info);
        expect(n.coordinate).not.toBe(info.coordinate);
        expect(n.pixel).not.toBe(info.pixel);
    });

    it('nulls out object/properties/index on a miss', () => {
        const n = normalizePickInfo({ picked: false, x: 1, y: 2, object: { should: 'not appear' } });
        expect(n.picked).toBe(false);
        expect(n.object).toBeNull();
        expect(n.properties).toBeNull();
        expect(n.index).toBeNull();
    });

    it('surfaces GeoJSON properties for picked features', () => {
        const feature = { type: 'Feature', geometry: { type: 'Point', coordinates: [0, 0] }, properties: { name: 'x' } };
        const n = normalizePickInfo({ picked: true, index: 0, object: feature, x: 0, y: 0 });
        expect(n.properties).toEqual({ name: 'x' });
        expect(n.object.type).toBe('Feature');
    });
});

describe('serializeObject', () => {
    it('passes through primitives and null', () => {
        expect(serializeObject(null)).toBeNull();
        expect(serializeObject(undefined)).toBeNull();
        expect(serializeObject(5)).toBe(5);
        expect(serializeObject('s')).toBe('s');
    });

    it('extracts only standard GeoJSON fields from features', () => {
        const feature = {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [1, 2] },
            properties: { a: 1 },
            id: 'f1',
            _internal: 'secret',
        };
        const s = serializeObject(feature);
        expect(s).toEqual({ type: 'Feature', geometry: { type: 'Point', coordinates: [1, 2] }, properties: { a: 1 }, id: 'f1' });
    });

    it('survives circular references', () => {
        const obj = { a: 1 };
        obj.self = obj;
        const s = serializeObject(obj);
        expect(s.a).toBe(1);
        expect(s.self).toBeUndefined();
    });

    it('drops functions and underscore-private keys', () => {
        const s = serializeObject({ keep: 1, _private: 2, fn: () => 3 });
        expect(s).toEqual({ keep: 1 });
    });

    it('handles nested arrays and objects', () => {
        const s = serializeObject({ list: [{ v: 1 }, { v: 2 }], nested: { deep: { x: 'y' } } });
        expect(s.list).toEqual([{ v: 1 }, { v: 2 }]);
        expect(s.nested.deep.x).toBe('y');
    });
});
