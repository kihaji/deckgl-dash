/**
 * Reorder layer configs according to a list of layer IDs (bottom to top).
 * Layers not mentioned in the order array are appended at the top.
 * Pure function extracted from DeckGL.react.js so it can be unit-tested.
 */
export function applyLayerOrder(configs, order) {
    const configById = {};
    for (const config of configs) {
        if (config.id) configById[config.id] = config;
    }
    const ordered = [];
    const placed = new Set();
    for (const id of order) {
        if (id in configById) {
            ordered.push(configById[id]);
            placed.add(id);
        }
    }
    for (const config of configs) {
        if (config.id && !placed.has(config.id)) ordered.push(config);
    }
    return ordered;
}
