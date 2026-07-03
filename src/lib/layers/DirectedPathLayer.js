/**
 * DirectedPathLayer - a CompositeLayer that draws a path plus evenly-spaced
 * direction-of-travel arrows along it.
 *
 * Renders two sublayers from a single config (so `opacity`, `pickable`, `visible`
 * etc. set on this layer propagate to both):
 *   1. the line  - MultiColorPathLayer when `multiColor`, else stock PathLayer
 *   2. the arrows - an IconLayer of arrowheads placed at a fixed SCREEN-PIXEL
 *      spacing along each path, rotated to the local travel direction.
 *
 * Arrows are placed in screen space (recomputed on zoom, not on pan) so spacing
 * and size stay constant at any zoom. Each arrow inherits the color of the path
 * segment it sits on (per-segment when `multiColor`), unless `arrowColor` overrides.
 * Arrows are non-pickable, so the layer picks as the single underlying track.
 *
 * Scaling design (issue #81): naive marker placement projected every vertex of
 * every path on every zoom tick. Instead, per-path geometry is cached ONCE per
 * data change in Web Mercator common space (viewport-independent): cumulative
 * arc lengths, per-segment angles, and a bounding box. With no pitch/bearing,
 * screen length = common length x viewport.scale, so each zoom tick only walks
 * precomputed lengths (float adds), culls off-screen paths by bbox, and
 * unprojects the markers actually placed. Markers are emitted as typed-array
 * binary attributes, skipping per-object accessor iteration in the IconLayer.
 * Pitched/rotated views fall back to the exact per-vertex projection path.
 */
import { CompositeLayer } from '@deck.gl/core';
import { IconLayer, PathLayer } from '@deck.gl/layers';
import MultiColorPathLayer from './MultiColorPathLayer';

// White arrowhead pointing east (+x) at angle 0, with a concave back (chevron-ish).
// White so IconLayer.getColor can tint it. Drawn on a 64x64 canvas, anchored at center.
const ARROW_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">' +
    '<path d="M14 12 L54 32 L14 52 L26 32 Z" fill="white"/></svg>';
const ARROW_ATLAS = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(ARROW_SVG)}`;
const ARROW_MAPPING = {
    arrow: { x: 0, y: 0, width: 64, height: 64, anchorX: 32, anchorY: 32, mask: true },
};

/** deck.gl-native binary path data: {length, attributes: {getPath, ...}, startIndices?} */
function isBinaryPathData(data) {
    return Boolean(data && !Array.isArray(data) && data.attributes && typeof data.length === 'number');
}

export default class DirectedPathLayer extends CompositeLayer {
    // Recompute markers on any change, including viewport changes (default
    // shouldUpdateState ignores viewport). The heavy recompute is gated in updateState.
    shouldUpdateState({ changeFlags }) {
        return changeFlags.somethingChanged;
    }

    updateState({ props, oldProps, changeFlags }) {
        const zoom = this.context.viewport ? this.context.viewport.zoom : null;
        const zoomChanged = this.state.lastZoom === undefined || Math.abs(zoom - this.state.lastZoom) > 1e-3;
        // Markers depend on geometry, zoom, styling and the per-path filter value — but NOT
        // on filterRange. The sliding time window is a GPU uniform, so animating it must not
        // re-project markers every frame; only recompute when a marker-relevant prop changes.
        const markerPropsChanged = changeFlags.dataChanged ||
            props.getPath !== oldProps.getPath ||
            props.getColor !== oldProps.getColor ||
            props.multiColor !== oldProps.multiColor ||
            props.arrowSpacing !== oldProps.arrowSpacing ||
            props.arrowColor !== oldProps.arrowColor ||
            props.getFilterValue !== oldProps.getFilterValue;
        if (markerPropsChanged) {
            this.setState({ pathCache: this._buildPathCache() });
        }
        if (markerPropsChanged || zoomChanged) {
            this.setState({ markers: this._computeMarkers(), lastZoom: zoom });
        }
    }

    /**
     * Viewport-INDEPENDENT per-path geometry, built once per data/style change:
     * common-space coords, cumulative arc lengths, per-segment screen angles
     * (exact while pitch = bearing = 0), resolved segment colors, filter value,
     * and a common-space bbox for culling. projectFlat is pure Web Mercator math,
     * so the cache survives every pan/zoom.
     */
    _buildPathCache() {
        const { data, getPath, getColor, multiColor, arrowColor, getFilterValue } = this.props;
        const { viewport } = this.context;
        if (!data || !viewport || !viewport.projectFlat) {
            return null;
        }
        if (isBinaryPathData(data)) {
            return this._buildPathCacheBinary(data, viewport);
        }
        const items = Array.isArray(data) ? data : [];
        const resolvePath = typeof getPath === 'function' ? getPath : (o) => o.path;
        const resolveColor = typeof getColor === 'function' ? getColor : () => getColor;
        const resolveFilter = typeof getFilterValue === 'function' ? getFilterValue : null;

        const cache = [];
        for (const object of items) {
            const path = resolvePath(object);
            if (!Array.isArray(path) || path.length < 2) {
                continue;
            }
            const n = path.length;
            const lngLat = new Float64Array(n * 2);
            const common = new Float64Array(n * 2);
            const cum = new Float64Array(n);          // cumulative common-space length at each vertex
            const segAngle = new Float32Array(n - 1); // CCW degrees at bearing 0
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            for (let i = 0; i < n; i++) {
                lngLat[i * 2] = path[i][0];
                lngLat[i * 2 + 1] = path[i][1];
                const [cx, cy] = viewport.projectFlat([path[i][0], path[i][1]]);
                common[i * 2] = cx;
                common[i * 2 + 1] = cy;
                if (cx < minX) minX = cx;
                if (cy < minY) minY = cy;
                if (cx > maxX) maxX = cx;
                if (cy > maxY) maxY = cy;
                if (i > 0) {
                    const dx = cx - common[(i - 1) * 2];
                    const dy = cy - common[(i - 1) * 2 + 1];
                    cum[i] = cum[i - 1] + Math.hypot(dx, dy);
                    // Common-space y grows opposite to screen y, so the screen-space
                    // "-atan2(dyScreen, dx)" is atan2(dyCommon, dx) here.
                    segAngle[i - 1] = Math.atan2(dy, dx) * 180 / Math.PI;
                }
            }

            const colorVal = resolveColor(object);
            const perSegment = multiColor && Array.isArray(colorVal) && Array.isArray(colorVal[0]);
            const singleColor = Array.isArray(colorVal) && Array.isArray(colorVal[0]) ? colorVal[0] : colorVal;
            cache.push({
                lngLat, common, cum, segAngle,
                bbox: [minX, minY, maxX, maxY],
                colors: arrowColor ? null : (perSegment ? colorVal : null),
                colorAttr: null,
                singleColor: arrowColor || singleColor || [0, 0, 0, 255],
                filterValue: resolveFilter ? resolveFilter(object) : 0,
            });
        }
        return cache;
    }

    /**
     * Cache builder for deck.gl-native binary path data
     * ({length, attributes: {getPath, getColor?, getFilterValue?}, startIndices}).
     * Colors follow the stock-PathLayer binary convention: one per VERTEX, each
     * segment taking its leading vertex's color. The per-path filter value is the
     * first vertex's getFilterValue entry.
     */
    _buildPathCacheBinary(data, viewport) {
        const { arrowColor } = this.props;
        const pathAttr = data.attributes.getPath;
        if (!pathAttr || !pathAttr.value) {
            return null;
        }
        const posSize = pathAttr.size || 2;
        const verts = pathAttr.value;
        const totalVerts = verts.length / posSize;
        const si = data.startIndices || new Uint32Array([0]);
        const nPaths = data.startIndices ? data.length : 1;
        const colorAttrRaw = !arrowColor && data.attributes.getColor ? data.attributes.getColor : null;
        const fvAttr = data.attributes.getFilterValue || null;

        const cache = [];
        for (let p = 0; p < nPaths; p++) {
            const start = si[p];
            const end = p + 1 < nPaths ? si[p + 1] : totalVerts;
            const n = end - start;
            if (n < 2) {
                continue;
            }
            const lngLat = new Float64Array(n * 2);
            const common = new Float64Array(n * 2);
            const cum = new Float64Array(n);
            const segAngle = new Float32Array(n - 1);
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            for (let i = 0; i < n; i++) {
                const lng = verts[(start + i) * posSize];
                const lat = verts[(start + i) * posSize + 1];
                lngLat[i * 2] = lng;
                lngLat[i * 2 + 1] = lat;
                const [cx, cy] = viewport.projectFlat([lng, lat]);
                common[i * 2] = cx;
                common[i * 2 + 1] = cy;
                if (cx < minX) minX = cx;
                if (cy < minY) minY = cy;
                if (cx > maxX) maxX = cx;
                if (cy > maxY) maxY = cy;
                if (i > 0) {
                    const dx = cx - common[(i - 1) * 2];
                    const dy = cy - common[(i - 1) * 2 + 1];
                    cum[i] = cum[i - 1] + Math.hypot(dx, dy);
                    segAngle[i - 1] = Math.atan2(dy, dx) * 180 / Math.PI;
                }
            }
            cache.push({
                lngLat, common, cum, segAngle,
                bbox: [minX, minY, maxX, maxY],
                colors: null,
                // zero-copy view info: segment s colors come from vertex (start + s)
                colorAttr: colorAttrRaw ? { value: colorAttrRaw.value, size: colorAttrRaw.size || 4, base: start } : null,
                singleColor: arrowColor || [0, 0, 0, 255],
                filterValue: fvAttr ? fvAttr.value[start] : 0,
            });
        }
        return cache;
    }

    /** Resolve the arrow color for segment segIndex of cached path p. */
    _markerColor(p, segIndex) {
        if (p.colorAttr) {
            const { value, size, base } = p.colorAttr;
            const o = (base + segIndex) * size;
            return [value[o], value[o + 1], value[o + 2], size > 3 ? value[o + 3] : 255];
        }
        if (p.colors) {
            return p.colors[Math.min(segIndex, p.colors.length - 1)];
        }
        return p.singleColor;
    }

    _computeMarkers() {
        const { viewport } = this.context;
        const { pathCache } = this.state;
        const spacing = Math.max(Number(this.props.arrowSpacing) || 1, 1);
        if (!viewport || !pathCache || pathCache.length === 0) {
            return null;
        }
        // The common-space fast path is exact only for a top-down, north-up camera;
        // perspective (pitch) and rotation (bearing) fall back to full projection.
        if (viewport.pitch || viewport.bearing || !viewport.unprojectFlat) {
            return this._computeMarkersProjected(spacing);
        }

        // Pixels per common-space unit, probed empirically (constant across the
        // screen at pitch 0, and independent of deck.gl's internal scale conventions).
        const [clng, clat] = [viewport.longitude, viewport.latitude];
        const pA = viewport.project([clng, clat]);
        const pB = viewport.project([clng + 0.01, clat]);
        const fA = viewport.projectFlat([clng, clat]);
        const fB = viewport.projectFlat([clng + 0.01, clat]);
        const scale = Math.hypot(pB[0] - pA[0], pB[1] - pA[1]) / (Math.hypot(fB[0] - fA[0], fB[1] - fA[1]) || 1);
        if (!scale || !isFinite(scale)) {
            return this._computeMarkersProjected(spacing);
        }
        const spacingCommon = spacing / scale;

        // Viewport bounds in common space (+ half-spacing margin) for culling
        let cull = null;
        if (viewport.getBounds) {
            const [west, south, east, north] = viewport.getBounds();
            const [x0, y0] = viewport.projectFlat([west, south]);
            const [x1, y1] = viewport.projectFlat([east, north]);
            const margin = spacingCommon;
            cull = [Math.min(x0, x1) - margin, Math.min(y0, y1) - margin,
                    Math.max(x0, x1) + margin, Math.max(y0, y1) + margin];
        }

        // Growable plain arrays of numbers -> typed arrays once at the end
        const positions = [];
        const angles = [];
        const colors = [];
        const filterValues = [];

        for (const p of pathCache) {
            if (cull && (p.bbox[2] < cull[0] || p.bbox[0] > cull[2] || p.bbox[3] < cull[1] || p.bbox[1] > cull[3])) {
                continue;
            }
            const total = p.cum[p.cum.length - 1];
            let placedAny = false;
            let nextAt = spacingCommon / 2;
            let seg = 0;
            const emit = (at, segIndex) => {
                // interpolate in common space, then one unproject per marker
                const segStart = p.cum[segIndex];
                const segLen = p.cum[segIndex + 1] - segStart;
                const t = segLen > 0 ? (at - segStart) / segLen : 0;
                const x = p.common[segIndex * 2] + (p.common[(segIndex + 1) * 2] - p.common[segIndex * 2]) * t;
                const y = p.common[segIndex * 2 + 1] + (p.common[(segIndex + 1) * 2 + 1] - p.common[segIndex * 2 + 1]) * t;
                const [lng, lat] = viewport.unprojectFlat([x, y]);
                positions.push(lng, lat);
                angles.push(p.segAngle[segIndex]);
                const c = this._markerColor(p, segIndex);
                colors.push(c[0], c[1], c[2], c.length > 3 && !isNaN(c[3]) ? c[3] : 255);
                filterValues.push(p.filterValue);
            };
            while (nextAt <= total) {
                while (seg < p.cum.length - 2 && p.cum[seg + 1] < nextAt) {
                    seg++;
                }
                emit(nextAt, seg);
                placedAny = true;
                nextAt += spacingCommon;
            }
            // Ensure at least one arrow even when the whole path is shorter than half a spacing.
            if (!placedAny) {
                const mid = Math.max(0, Math.floor(p.cum.length / 2) - 1);  // middle segment, matching the projected fallback
                emit((p.cum[mid] + p.cum[mid + 1]) / 2, mid);
            }
        }

        return this._markersToBinary(positions, angles, colors, filterValues);
    }

    /** Exact fallback for pitched/rotated views: original per-vertex screen projection. */
    _computeMarkersProjected(spacing) {
        const { viewport } = this.context;
        const { pathCache } = this.state;
        const positions = [];
        const angles = [];
        const colors = [];
        const filterValues = [];

        for (const p of pathCache) {
            const nPts = p.lngLat.length / 2;
            const screen = new Array(nPts);
            for (let i = 0; i < nPts; i++) {
                screen[i] = viewport.project([p.lngLat[i * 2], p.lngLat[i * 2 + 1]]);
            }
            let walked = 0;
            let nextAt = spacing / 2;
            let placedAny = false;
            const pushMarker = (sx, sy, angle, segIndex) => {
                const lngLat = viewport.unproject([sx, sy]);
                positions.push(lngLat[0], lngLat[1]);
                angles.push(angle);
                const c = this._markerColor(p, segIndex);
                colors.push(c[0], c[1], c[2], c.length > 3 && !isNaN(c[3]) ? c[3] : 255);
                filterValues.push(p.filterValue);
            };
            for (let i = 1; i < screen.length; i++) {
                const [x0, y0] = screen[i - 1];
                const [x1, y1] = screen[i];
                const dx = x1 - x0;
                const dy = y1 - y0;
                const segLen = Math.hypot(dx, dy);
                if (segLen === 0) {
                    continue;
                }
                // Screen bearing -> CCW degrees (screen y points down, so negate).
                const angle = -Math.atan2(dy, dx) * 180 / Math.PI;
                while (walked + segLen >= nextAt) {
                    const t = (nextAt - walked) / segLen;
                    pushMarker(x0 + dx * t, y0 + dy * t, angle, i - 1);
                    placedAny = true;
                    nextAt += spacing;
                }
                walked += segLen;
            }
            if (!placedAny) {
                const i = Math.max(1, Math.floor(nPts / 2));
                const [x0, y0] = screen[i - 1];
                const [x1, y1] = screen[i];
                const angle = -Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
                pushMarker((x0 + x1) / 2, (y0 + y1) / 2, angle, i - 1);
            }
        }
        return this._markersToBinary(positions, angles, colors, filterValues);
    }

    /** Emit markers as deck.gl binary attributes — no per-object accessor iteration. */
    _markersToBinary(positions, angles, colors, filterValues) {
        const length = angles.length;
        return {
            length,
            attributes: {
                getPosition: { value: new Float64Array(positions), size: 2 },
                getAngle: { value: new Float32Array(angles), size: 1 },
                getColor: { value: new Uint8Array(colors), size: 4 },
            },
            filterValues: new Float32Array(filterValues),
        };
    }

    renderLayers() {
        const {
            data, getPath, getColor, getWidth, multiColor,
            widthUnits, widthScale, widthMinPixels, widthMaxPixels, capRounded, jointRounded,
            arrowSize, getFilterValue,
        } = this.props;

        // When a DataFilterExtension is attached (time slider), deck.gl auto-forwards this
        // layer's getFilterValue + filterRange to both sublayers via getSubLayerProps. That is
        // correct for the LINE (its data is the path objects), so we let it flow through.
        const hasFilter = typeof getFilterValue === 'function';

        // Binary data: per-vertex colors are native to the stock PathLayer, so the
        // MultiColorPathLayer subclass (a JSON-rows accessor mechanism) is bypassed.
        const isBinary = isBinaryPathData(data);
        const LineLayer = (multiColor && !isBinary) ? MultiColorPathLayer : PathLayer;
        const pathSub = new LineLayer(this.getSubLayerProps({
            id: 'path',
            data,
            _pathType: this.props._pathType,
            getPath,
            getColor,
            getWidth,
            widthUnits,
            widthScale,
            widthMinPixels,
            widthMaxPixels,
            capRounded,
            jointRounded,
        }));

        const markers = this.state.markers || { length: 0, attributes: {} };
        const arrowProps = this.getSubLayerProps({
            id: 'arrows',
            data: { length: markers.length, attributes: markers.attributes },
            iconAtlas: ARROW_ATLAS,
            iconMapping: ARROW_MAPPING,
            getIcon: () => 'arrow',
            sizeUnits: 'pixels',
            getSize: arrowSize,
            billboard: true,
            pickable: false,
        });
        // The arrow sublayer's data is computed markers (not paths), so the auto-forwarded
        // parent getFilterValue would read a nonexistent field. Override it (AFTER
        // getSubLayerProps, which is where the extension injects the parent's accessor) with
        // the per-marker filter values, so arrows fade with their line. Binary paths carry
        // the filter as a data attribute rather than an accessor prop.
        const binaryHasFilter = isBinary && Boolean(data.attributes.getFilterValue);
        if ((hasFilter || binaryHasFilter) && markers.filterValues) {
            arrowProps.data = {
                length: markers.length,
                attributes: { ...markers.attributes, getFilterValue: { value: markers.filterValues, size: 1 } },
            };
        }
        const arrowSub = new IconLayer(arrowProps);

        return [pathSub, arrowSub];
    }
}

DirectedPathLayer.layerName = 'DirectedPathLayer';
DirectedPathLayer.defaultProps = {
    getPath: { type: 'accessor', value: (d) => d.path },
    getColor: { type: 'accessor', value: [0, 0, 0, 255] },
    getWidth: { type: 'accessor', value: 1 },
    widthUnits: 'meters',
    widthScale: 1,
    widthMinPixels: 0,
    widthMaxPixels: Number.MAX_SAFE_INTEGER,
    capRounded: false,
    jointRounded: false,
    multiColor: false,
    arrowSpacing: { type: 'number', value: 100, min: 1 },
    arrowSize: { type: 'number', value: 18, min: 1 },
    arrowColor: { type: 'color', value: null, optional: true },
    _pathType: null,  // forwarded to the line sublayer; binary paths should set 'open' or 'loop'
};
