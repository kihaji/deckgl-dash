/**
 * Event Handler - Normalizes deck.gl events for Dash callbacks
 */

/**
 * Check if a specific event type is enabled
 * @param {string} eventType - Event type ('click', 'hover', 'viewStateChange', 'dataLoad', 'dataLoadError')
 * @param {boolean|Array} enableEvents - Event configuration
 * @returns {boolean}
 */
export function isEventEnabled(eventType, enableEvents) {
    if (enableEvents === true) {
        return true;
    }
    if (Array.isArray(enableEvents)) {
        return enableEvents.includes(eventType);
    }
    return false;
}

/**
 * Normalize a deck.gl picking info object for Dash callbacks
 */
export function normalizePickInfo(info) {
    if (!info) {
        return null;
    }
    const picked = Boolean(info.picked);
    // Serialize the object only when a feature was picked
    const serializedObject = picked ? serializeObject(info.object) : null;
    const properties = picked ? (serializedObject?.properties || null) : null;

    return {
        picked,
        index: picked && typeof info.index === 'number' ? info.index : null,
        layerId: info.layer?.id || null,
        coordinate: Array.isArray(info.coordinate) ? [...info.coordinate] : null,
        x: typeof info.x === 'number' ? info.x : null,
        y: typeof info.y === 'number' ? info.y : null,
        pixel: Array.isArray(info.pixel) ? [...info.pixel] : [info.x, info.y],
        object: serializedObject,
        properties: properties,
    };
}

/**
 * Serialize an object for JSON transport to Python
 * Uses JSON.stringify with a custom replacer to handle cycles
 */
export function serializeObject(obj) {
    if (obj === null || obj === undefined) {
        return null;
    }
    // For GeoJSON features, extract only the standard GeoJSON properties
    if (obj && typeof obj === 'object' && obj.type === 'Feature') {
        return {
            type: 'Feature',
            geometry: safeClone(obj.geometry),
            properties: safeClone(obj.properties) || {},
            id: obj.id,
        };
    }
    // For other objects, do a safe clone
    return safeClone(obj);
}

/**
 * Safely clone an object, handling circular references
 */
function safeClone(obj) {
    if (obj === null || obj === undefined) {
        return null;
    }
    if (typeof obj !== 'object') {
        return obj;
    }
    try {
        // Use JSON round-trip with cycle detection
        const seen = new WeakSet();
        return JSON.parse(JSON.stringify(obj, (key, value) => {
            // Skip functions and symbols
            if (typeof value === 'function' || typeof value === 'symbol') {
                return undefined;
            }
            // Skip private properties
            if (key.startsWith('_')) {
                return undefined;
            }
            // Handle objects - check for cycles
            if (typeof value === 'object' && value !== null) {
                if (seen.has(value)) {
                    return undefined; // Skip circular reference
                }
                seen.add(value);
            }
            return value;
        }));
    } catch (e) {
        // If JSON serialization fails, return a minimal safe object
        console.warn('Failed to serialize object:', e);
        return null;
    }
}
