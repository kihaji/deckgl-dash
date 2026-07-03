/**
 * Zoom-gated layer visibility: per-layer `visibleMinZoom`/`visibleMaxZoom` config
 * keys fold into deck.gl `visible` based on the current map zoom (LOD-style
 * dashboards — e.g. points only past zoom 10).
 *
 * Named after deck.gl 9.3's TileLayer props of the same name; `minZoom`/`maxZoom`
 * are NOT used for gating because tile layers give them data-range semantics.
 *
 * The MapLibre `zoom` event fires every frame, so callers compare zoomGateKey()
 * results and only push layers when some layer's in-range state actually flips.
 */

/**
 * Extract gating descriptors from layer configs and return configs with the
 * gating keys stripped (deck.gl layers don't know them, except tile layers
 * in 9.3 — we gate uniformly at the component level for both render modes).
 */
export function extractZoomGates(configs) {
    const gates = [];
    let stripped = configs;
    if (Array.isArray(configs) && configs.some(c => c && (c.visibleMinZoom != null || c.visibleMaxZoom != null))) {
        stripped = configs.map(c => {
            if (!c || (c.visibleMinZoom == null && c.visibleMaxZoom == null)) {
                return c;
            }
            const { visibleMinZoom, visibleMaxZoom, ...rest } = c;
            gates.push({
                id: c.id,
                min: visibleMinZoom != null ? visibleMinZoom : null,
                max: visibleMaxZoom != null ? visibleMaxZoom : null,
                baseVisible: c.visible !== false,
            });
            return rest;
        });
    }
    return { configs: stripped, gates };
}

function inRange(gate, zoom) {
    return (gate.min == null || zoom >= gate.min) && (gate.max == null || zoom <= gate.max);
}

/**
 * Compact change-key: one bit per gated layer. Callers push new layers only
 * when the key changes, so per-frame zoom events cause no setProps churn.
 */
export function zoomGateKey(gates, zoom) {
    if (!gates || gates.length === 0) {
        return '';
    }
    return gates.map(g => `${g.id}:${inRange(g, zoom) ? 1 : 0}`).join('|');
}

/**
 * Return a new layers array where each gated layer is cloned with `visible`
 * folded from its stored base visibility and the current zoom. Non-gated
 * layers pass through untouched (referentially stable).
 */
export function applyZoomVisibility(layers, gates, zoom) {
    if (!gates || gates.length === 0 || !Array.isArray(layers)) {
        return layers;
    }
    const gateById = {};
    for (const g of gates) {
        gateById[g.id] = g;
    }
    return layers.map(layer => {
        const gate = layer && gateById[layer.id];
        if (!gate) {
            return layer;
        }
        return layer.clone({ visible: gate.baseVisible && inRange(gate, zoom) });
    });
}
