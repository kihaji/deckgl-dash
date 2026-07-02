import { describe, it, expect } from 'vitest';
import { WebMercatorViewport } from '@deck.gl/core';
import DirectedPathLayer from '../DirectedPathLayer';

const PATHS = [
    { path: [[-122.45, 37.77], [-122.43, 37.78], [-122.41, 37.77], [-122.38, 37.79]] },
    { path: [[-122.44, 37.74], [-122.42, 37.73]] },
    // far away — culled by the fast path, still processed by the fallback
    { path: [[10.0, 50.0], [10.1, 50.05]] },
];

// Drive the real methods on a prototype-linked harness — no deck lifecycle needed.
// defineProperty shadows deck.gl Layer's props/state accessors with plain values.
function makeHarness(viewport, props) {
    const h = Object.create(DirectedPathLayer.prototype);
    Object.defineProperty(h, 'props', { value: {
        data: PATHS,
        getPath: (d) => d.path,
        getColor: [10, 20, 30, 255],
        multiColor: false,
        arrowSpacing: 60,
        arrowColor: null,
        getFilterValue: null,
        ...props,
    }, writable: true });
    Object.defineProperty(h, 'context', { value: { viewport }, writable: true });
    Object.defineProperty(h, 'state', { value: {}, writable: true });
    return h;
}

function compute(viewport, props) {
    const h = makeHarness(viewport, props);
    h.state.pathCache = h._buildPathCache();
    return {
        fast: h._computeMarkers(),
        projected: h._computeMarkersProjected(Math.max(Number(h.props.arrowSpacing) || 1, 1)),
    };
}

describe('DirectedPathLayer marker computation (issue #81)', () => {
    const viewport = new WebMercatorViewport({
        width: 600, height: 500, longitude: -122.42, latitude: 37.77, zoom: 12, pitch: 0, bearing: 0,
    });

    it('fast common-space path matches the exact projected fallback at pitch 0', () => {
        // On-screen paths only: the fallback also processes culled far-away paths,
        // so restrict the parity comparison to identical work.
        const { fast, projected } = compute(viewport, { data: PATHS.slice(0, 2) });
        expect(projected.length).toBe(fast.length);
        expect(fast.length).toBeGreaterThan(5);
        for (let i = 0; i < fast.length; i++) {
            expect(fast.attributes.getPosition.value[i * 2]).toBeCloseTo(projected.attributes.getPosition.value[i * 2], 6);
            expect(fast.attributes.getPosition.value[i * 2 + 1]).toBeCloseTo(projected.attributes.getPosition.value[i * 2 + 1], 6);
            expect(fast.attributes.getAngle.value[i]).toBeCloseTo(projected.attributes.getAngle.value[i], 3);
        }
    });

    it('culls paths outside the viewport in the fast path', () => {
        const { fast } = compute(viewport, {});
        for (let i = 0; i < fast.length; i++) {
            const lng = fast.attributes.getPosition.value[i * 2];
            expect(lng).toBeLessThan(-100); // nothing from the path at lng 10
        }
    });

    it('places at least one arrow on very short paths', () => {
        const harness = makeHarness(viewport, { arrowSpacing: 10000 });
        harness.props.data = [{ path: [[-122.421, 37.771], [-122.4209, 37.7711]] }];
        harness.state.pathCache = harness._buildPathCache();
        const fast = harness._computeMarkers();
        expect(fast.length).toBe(1);
    });

    it('per-segment colors land on the right markers', () => {
        const colors = [[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]];
        const harness = makeHarness(viewport, {
            multiColor: true,
            getColor: () => colors,
        });
        harness.props.data = [PATHS[0]];
        harness.state.pathCache = harness._buildPathCache();
        const fast = harness._computeMarkers();
        expect(fast.length).toBeGreaterThan(2);
        const c = fast.attributes.getColor.value;
        const seen = new Set();
        for (let i = 0; i < fast.length; i++) {
            seen.add(`${c[i * 4]},${c[i * 4 + 1]},${c[i * 4 + 2]}`);
        }
        expect(seen.size).toBeGreaterThan(1); // markers picked up different segment colors
    });

    it('uses the exact fallback under pitch/bearing', () => {
        const tilted = new WebMercatorViewport({
            width: 600, height: 500, longitude: -122.42, latitude: 37.77, zoom: 12, pitch: 40, bearing: 30,
        });
        const harness = makeHarness(tilted, {});
        harness.props.data = [PATHS[0]];
        harness.state.pathCache = harness._buildPathCache();
        const markers = harness._computeMarkers();
        expect(markers.length).toBeGreaterThan(0);
        expect(markers.attributes.getPosition.value).toBeInstanceOf(Float64Array);
    });
});
