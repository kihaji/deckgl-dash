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

export default class DirectedPathLayer extends CompositeLayer {
    // Recompute markers on any change, including viewport changes (default
    // shouldUpdateState ignores viewport). The heavy recompute is gated in updateState.
    shouldUpdateState({ changeFlags }) {
        return changeFlags.somethingChanged;
    }

    updateState({ changeFlags }) {
        const zoom = this.context.viewport ? this.context.viewport.zoom : null;
        const zoomChanged = this.state.lastZoom === undefined || Math.abs(zoom - this.state.lastZoom) > 1e-3;
        // Marker screen-spacing only depends on data and zoom (pure pan preserves pixel spacing).
        if (changeFlags.dataChanged || changeFlags.propsChanged || zoomChanged) {
            this.setState({ markers: this._computeMarkers(), lastZoom: zoom });
        }
    }

    _computeMarkers() {
        const { data, getPath, getColor, multiColor, arrowSpacing, arrowColor } = this.props;
        const { viewport } = this.context;
        if (!data || !viewport) {
            return [];
        }
        const spacing = Math.max(Number(arrowSpacing) || 1, 1);
        const items = Array.isArray(data) ? data : (data.length !== undefined ? Array.from(data) : []);
        const markers = [];

        const resolvePath = typeof getPath === 'function' ? getPath : (o) => o.path;
        const resolveColor = typeof getColor === 'function' ? getColor : () => getColor;

        for (const object of items) {
            const path = resolvePath(object);
            if (!Array.isArray(path) || path.length < 2) {
                continue;
            }
            const colorVal = resolveColor(object);
            const perSegment = multiColor && Array.isArray(colorVal) && Array.isArray(colorVal[0]);
            const singleColor = Array.isArray(colorVal) && Array.isArray(colorVal[0]) ? colorVal[0] : colorVal;
            const segColor = (segIndex) => {
                if (arrowColor) return arrowColor;
                if (perSegment) return colorVal[Math.min(segIndex, colorVal.length - 1)];
                return singleColor;
            };

            const screen = path.map((p) => viewport.project([p[0], p[1]]));
            let walked = 0;
            let nextAt = spacing / 2; // first arrow half a spacing in
            let placedAny = false;

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
                    const sx = x0 + dx * t;
                    const sy = y0 + dy * t;
                    const lngLat = viewport.unproject([sx, sy]);
                    markers.push({ position: [lngLat[0], lngLat[1]], angle, color: segColor(i - 1) });
                    placedAny = true;
                    nextAt += spacing;
                }
                walked += segLen;
            }

            // Ensure at least one arrow even when the whole path is shorter than half a spacing.
            if (!placedAny) {
                const i = Math.max(1, Math.floor(path.length / 2));
                const [x0, y0] = screen[i - 1];
                const [x1, y1] = screen[i];
                const angle = -Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
                const lngLat = viewport.unproject([(x0 + x1) / 2, (y0 + y1) / 2]);
                markers.push({ position: [lngLat[0], lngLat[1]], angle, color: segColor(i - 1) });
            }
        }
        return markers;
    }

    renderLayers() {
        const {
            data, getPath, getColor, getWidth, multiColor,
            widthUnits, widthScale, widthMinPixels, widthMaxPixels, capRounded, jointRounded,
            arrowSize,
        } = this.props;

        const LineLayer = multiColor ? MultiColorPathLayer : PathLayer;
        const pathSub = new LineLayer(this.getSubLayerProps({
            id: 'path',
            data,
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

        const arrowSub = new IconLayer(this.getSubLayerProps({
            id: 'arrows',
            data: this.state.markers || [],
            iconAtlas: ARROW_ATLAS,
            iconMapping: ARROW_MAPPING,
            getIcon: () => 'arrow',
            sizeUnits: 'pixels',
            getSize: arrowSize,
            billboard: true,
            getPosition: (m) => m.position,
            getAngle: (m) => m.angle,
            getColor: (m) => m.color,
            pickable: false,
        }));

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
};
