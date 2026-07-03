import { describe, it, expect } from 'vitest';
import {
    AVAILABLE_SCALES, parseScaleAccessor, computeDomain, createColorScaleAccessor, isScaleAccessor, colorRangeFromScale,
} from '../colorScales';

describe('parseScaleAccessor', () => {
    it('rejects non-scale values', () => {
        expect(parseScaleAccessor('@@=properties.x')).toBeNull();
        expect(parseScaleAccessor(42)).toBeNull();
        expect(parseScaleAccessor('@@scale(')).toBeNull();
    });

    it('parses the minimal form', () => {
        const c = parseScaleAccessor('@@scale(viridis, properties.count)');
        expect(c.scaleName).toBe('viridis');
        expect(c.propertyPath).toBe('properties.count');
        expect(c.min).toBeNull();
        expect(c.max).toBeNull();
        expect(c.alpha).toBe(255);
    });

    it('parses explicit domain and alpha', () => {
        const c = parseScaleAccessor('@@scale(OrRd, properties.value, 0, 1000, 200)');
        expect(c.min).toBe(0);
        expect(c.max).toBe(1000);
        expect(c.alpha).toBe(200);
    });

    it('parses chained modifiers', () => {
        const c = parseScaleAccessor('@@scale(plasma:log:reverse, properties.v, 1, 100)');
        expect(c.modifiers).toEqual({ reverse: true, log: true, sqrt: false });
    });

    it('rejects unknown scale names and inverted domains', () => {
        expect(parseScaleAccessor('@@scale(nope, properties.v)')).toBeNull();
        expect(parseScaleAccessor('@@scale(viridis, properties.v, 100, 1)')).toBeNull();
    });
});

describe('isScaleAccessor', () => {
    it('detects @@scale strings only', () => {
        expect(isScaleAccessor('@@scale(viridis, v)')).toBe(true);
        expect(isScaleAccessor('@@=v')).toBe(false);
        expect(isScaleAccessor(7)).toBe(false);
    });
});

describe('computeDomain', () => {
    it('finds min/max, skipping non-numeric values', () => {
        const data = [{ v: 3 }, { v: 'x' }, { v: -2 }, { v: NaN }, { v: 10 }];
        expect(computeDomain(data, d => d.v)).toEqual({ min: -2, max: 10 });
    });

    it('returns 0..1 for empty/non-numeric data and pads equal min/max', () => {
        expect(computeDomain([], d => d.v)).toEqual({ min: 0, max: 1 });
        expect(computeDomain([{ v: 5 }], d => d.v)).toEqual({ min: 4.5, max: 5.5 });
    });
});

describe('createColorScaleAccessor', () => {
    const config = { scaleName: 'viridis', modifiers: { reverse: false, log: false, sqrt: false }, propertyPath: 'v', min: 0, max: 10, alpha: 255 };

    it('maps domain extremes to scale endpoint colors', () => {
        const fn = createColorScaleAccessor(config, []);
        const low = fn({ v: 0 });
        const high = fn({ v: 10 });
        expect(low).toHaveLength(4);
        expect(low).not.toEqual(high);
        // viridis starts dark purple (#440154) and ends yellow (#fde725)
        expect(low[2]).toBeGreaterThan(low[1]);   // blue > green at the low end
        expect(high[0]).toBeGreaterThan(high[2]); // red > blue at the high end
    });

    it('returns gray for invalid values', () => {
        const fn = createColorScaleAccessor(config, []);
        expect(fn({ v: 'not-a-number' })).toEqual([128, 128, 128, 255]);
    });

    it('auto-computes the domain from data when min/max are null', () => {
        const cfg = { ...config, min: null, max: null };
        const fn = createColorScaleAccessor(cfg, [{ v: 0 }, { v: 100 }]);
        expect(fn({ v: 0 })).not.toEqual(fn({ v: 100 }));
    });
});

describe('colorRangeFromScale', () => {
    it('generates the requested number of RGB colors for every advertised scale', () => {
        for (const name of AVAILABLE_SCALES) {
            const colors = colorRangeFromScale(name, 5);
            expect(colors).toHaveLength(5);
            for (const c of colors) {
                expect(c).toHaveLength(3);
                for (const ch of c) {
                    expect(ch).toBeGreaterThanOrEqual(0);
                    expect(ch).toBeLessThanOrEqual(255);
                }
            }
        }
    });

    it('reverses when asked', () => {
        const fwd = colorRangeFromScale('viridis', 4);
        const rev = colorRangeFromScale('viridis', 4, { reverse: true });
        expect(rev).toEqual([...fwd].reverse());
    });
});
