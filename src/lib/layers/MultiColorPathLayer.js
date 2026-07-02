/**
 * MultiColorPathLayer - PathLayer subclass supporting per-segment coloring.
 *
 * deck.gl's stock PathLayer paints a single color per whole path. This subclass
 * (the documented deck.gl "subclassed-layers" pattern) overrides the instanced
 * `instanceColors` attribute so `getColor` may return EITHER:
 *   - a single RGBA array  -> the whole path uses that color, or
 *   - an array of RGBA arrays -> one color per segment (N points => N-1 segments).
 *
 * Each path remains a single pickable object.
 */
import { PathLayer } from '@deck.gl/layers';

export default class MultiColorPathLayer extends PathLayer {
    initializeState() {
        super.initializeState();
        // Replace PathLayer's built-in color attribute with our per-segment updater.
        this.getAttributeManager().addInstanced({
            instanceColors: {
                size: 4,
                type: 'unorm8',
                normalized: true,
                update: this.calculateColors,
            },
        });
    }

    calculateColors(attribute) {
        const { data, getPath, getColor } = this.props;
        const { value } = attribute;

        let i = 0;
        for (const object of data) {
            const path = getPath(object);
            const color = getColor(object);

            if (Array.isArray(color[0])) {
                // Per-segment colors: expect one color per segment (N points => N-1 segments).
                if (color.length !== path.length - 1) {
                     
                    console.warn(
                        `MultiColorPathLayer: getColor returned ${color.length} colors for a path ` +
                        `with ${path.length} points (expected ${path.length - 1}). Rendering may be misaligned.`
                    );
                }
                for (const segmentColor of color) {
                    value[i++] = segmentColor[0];
                    value[i++] = segmentColor[1];
                    value[i++] = segmentColor[2];
                    value[i++] = isNaN(segmentColor[3]) ? 255 : segmentColor[3];
                }
            } else {
                // Single color for the whole path: repeat it across every segment.
                for (let ptIndex = 1; ptIndex < path.length; ptIndex++) {
                    value[i++] = color[0];
                    value[i++] = color[1];
                    value[i++] = color[2];
                    value[i++] = isNaN(color[3]) ? 255 : color[3];
                }
            }
        }
    }
}

MultiColorPathLayer.layerName = 'MultiColorPathLayer';
