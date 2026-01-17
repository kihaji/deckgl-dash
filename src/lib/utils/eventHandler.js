/**
 * Event Handler - Normalizes deck.gl events for Dash callbacks
 * Handles click, hover, and drag events with consistent output format
 */

/**
 * Normalize a deck.gl picking info object for Dash callbacks
 * @param {Object} info - deck.gl picking info object
 * @returns {Object|null} Normalized event info or null if no valid pick
 */
export function normalizePickInfo(info) {
    if (!info || !info.picked) {
        return null;
    }
    const normalized = {
        // Basic pick info
        picked: true,
        index: info.index,
        layerId: info.layer?.id || null,
        // Coordinates
        coordinate: info.coordinate || null,
        x: info.x,
        y: info.y,
        // Pixel coordinates
        pixel: info.pixel || [info.x, info.y],
        // Object data (the actual feature/data item)
        object: serializeObject(info.object),
        // For GeoJSON features
        properties: info.object?.properties || null,
        // Source layer for MVT/Tile layers
        sourceLayer: info.sourceLayer || null,
    };
    return normalized;
}

/**
 * Serialize an object for JSON transport to Python
 * Handles GeoJSON features, plain objects, and primitives
 * @param {*} obj - Object to serialize
 * @returns {*} Serializable version of the object
 */
function serializeObject(obj) {
    if (obj === null || obj === undefined) {
        return null;
    }
    // Handle primitives
    if (typeof obj !== 'object') {
        return obj;
    }
    // Handle arrays
    if (Array.isArray(obj)) {
        return obj.map(item => serializeObject(item));
    }
    // Handle GeoJSON features
    if (obj.type === 'Feature') {
        return {
            type: 'Feature',
            geometry: obj.geometry,
            properties: obj.properties || {},
            id: obj.id,
        };
    }
    // Handle plain objects - only include serializable properties
    const serialized = {};
    for (const [key, value] of Object.entries(obj)) {
        // Skip functions, symbols, and other non-serializable types
        if (typeof value === 'function' || typeof value === 'symbol') {
            continue;
        }
        // Skip internal/private properties
        if (key.startsWith('_')) {
            continue;
        }
        // Recursively serialize nested objects (with depth limit)
        try {
            serialized[key] = serializeObject(value);
        } catch (e) {
            // Skip properties that fail to serialize
            console.warn(`Failed to serialize property ${key}:`, e);
        }
    }
    return serialized;
}

/**
 * Create a click event handler that updates Dash props
 * @param {Function} setProps - Dash setProps function
 * @param {boolean|Array} enableEvents - Event configuration
 * @returns {Function} Click handler function
 */
export function createClickHandler(setProps, enableEvents) {
    if (!isEventEnabled('click', enableEvents)) {
        return undefined;
    }
    return (info, event) => {
        const normalized = normalizePickInfo(info);
        setProps({
            clickInfo: normalized,
            clickEvent: {
                timestamp: Date.now(),
                srcEvent: event?.srcEvent ? {
                    clientX: event.srcEvent.clientX,
                    clientY: event.srcEvent.clientY,
                    button: event.srcEvent.button,
                } : null,
            },
        });
    };
}

/**
 * Create a hover event handler that updates Dash props
 * @param {Function} setProps - Dash setProps function
 * @param {boolean|Array} enableEvents - Event configuration
 * @returns {Function} Hover handler function
 */
export function createHoverHandler(setProps, enableEvents) {
    if (!isEventEnabled('hover', enableEvents)) {
        return undefined;
    }
    return (info) => {
        const normalized = normalizePickInfo(info);
        setProps({
            hoverInfo: normalized,
        });
    };
}

/**
 * Create a drag event handler for view state changes
 * @param {Function} setProps - Dash setProps function
 * @param {boolean|Array} enableEvents - Event configuration
 * @returns {Function} View state change handler
 */
export function createViewStateChangeHandler(setProps, enableEvents) {
    if (!isEventEnabled('viewStateChange', enableEvents)) {
        return undefined;
    }
    return ({ viewState }) => {
        setProps({
            viewState: {
                longitude: viewState.longitude,
                latitude: viewState.latitude,
                zoom: viewState.zoom,
                pitch: viewState.pitch || 0,
                bearing: viewState.bearing || 0,
            },
        });
    };
}

/**
 * Check if a specific event type is enabled
 * @param {string} eventType - Event type ('click', 'hover', 'viewStateChange')
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
 * Get all enabled event types
 * @param {boolean|Array} enableEvents - Event configuration
 * @returns {Array} Array of enabled event type strings
 */
export function getEnabledEvents(enableEvents) {
    const allEvents = ['click', 'hover', 'viewStateChange'];
    if (enableEvents === true) {
        return allEvents;
    }
    if (Array.isArray(enableEvents)) {
        return enableEvents.filter(e => allEvents.includes(e));
    }
    return [];
}
