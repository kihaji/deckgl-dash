/**
 * Time-filter helpers for the GPU sliding-window animation (DataFilterExtension).
 * Pure functions extracted from DeckGL.react.js so they can be unit-tested.
 */
import { DataFilterExtension } from '@deck.gl/extensions';

/**
 * Compute the GPU filter bounds for a sliding window ending at head time T.
 * Returns the hard `range` ([T-window, T]) and an optional `soft` fade range.
 */
export function computeFilterRange(T, tf) {
    const w = tf.window || 0;
    const range = [T - w, T];
    const soft = (typeof tf.softEdge === 'number' && tf.softEdge > 0)
        ? [T - w - tf.softEdge, T + tf.softEdge]
        : null;
    return { range, soft };
}

/**
 * Decide whether a layer should receive the time filter range.
 * Honors an explicit `layerIds` allowlist, otherwise auto-detects any layer
 * carrying a DataFilterExtension (so basemap/tile layers are never filtered).
 */
export function isFilterTarget(layer, tf) {
    if (!layer) return false;
    if (Array.isArray(tf.layerIds)) {
        return tf.layerIds.includes(layer.id);
    }
    const exts = layer.props && layer.props.extensions;
    return Array.isArray(exts) && exts.some(e => e instanceof DataFilterExtension);
}

/**
 * Return a new layers array where each filter-target layer is cloned with the
 * window's `filterRange` (and `filterSoftRange`). `layer.clone` only overrides a
 * GPU uniform — no re-tessellation — so this is cheap to call every frame.
 */
export function applyRangeToLayers(layers, T, tf) {
    if (!tf || !Array.isArray(layers)) return layers;
    const { range, soft } = computeFilterRange(T, tf);
    return layers.map(layer => {
        if (!isFilterTarget(layer, tf)) return layer;
        const overrides = soft ? { filterRange: range, filterSoftRange: soft } : { filterRange: range };
        return layer.clone(overrides);
    });
}

/** Resolve the head time used for the current render (paused -> current; playing -> live ref). */
export function resolveHeadTime(tf, headRef) {
    if (tf && !tf.playing && typeof tf.current === 'number') return tf.current;
    if (headRef != null) return headRef;
    if (tf && typeof tf.current === 'number') return tf.current;
    if (tf && Array.isArray(tf.domain)) return tf.domain[0] + (tf.window || 0);
    return 0;
}
