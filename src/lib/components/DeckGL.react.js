import React, { useState, useCallback, useMemo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { DeckGL as DeckGLComponent } from '@deck.gl/react';
import { createLayers } from '../utils/layerRegistry';
import { createClickHandler, createHoverHandler, createViewStateChangeHandler, isEventEnabled } from '../utils/eventHandler';

/**
 * DeckGL component for Plotly Dash
 * A high-performance WebGL-powered visualization component wrapping deck.gl
 * Supports all deck.gl layer types via JSON configuration
 */
const DEFAULT_VIEW_STATE = {
    longitude: -122.4,
    latitude: 37.8,
    zoom: 11,
    pitch: 0,
    bearing: 0,
};

const DeckGL = ({
    id,
    layers = [],
    initialViewState = DEFAULT_VIEW_STATE,
    viewState: controlledViewState,
    controller = true,
    enableEvents = false,
    tooltip = false,
    style = {},
    setProps,
}) => {

    // Internal view state for uncontrolled mode
    const [internalViewState, setInternalViewState] = useState(initialViewState);

    // Use controlled view state if provided, otherwise use internal
    const currentViewState = controlledViewState || internalViewState;

    // Update internal view state when initialViewState changes (uncontrolled mode)
    useEffect(() => {
        if (!controlledViewState && initialViewState) {
            setInternalViewState(initialViewState);
        }
    }, [initialViewState, controlledViewState]);

    // Create deck.gl layers from JSON configs
    const deckLayers = useMemo(() => {
        return createLayers(layers || []);
    }, [layers]);

    // View state change handler (for both internal state and Dash callbacks)
    const handleViewStateChange = useCallback(({ viewState: newViewState }) => {
        // Update internal state for uncontrolled mode
        if (!controlledViewState) {
            setInternalViewState(newViewState);
        }
        // Fire Dash callback if viewStateChange events are enabled
        if (isEventEnabled('viewStateChange', enableEvents) && setProps) {
            setProps({
                viewState: {
                    longitude: newViewState.longitude,
                    latitude: newViewState.latitude,
                    zoom: newViewState.zoom,
                    pitch: newViewState.pitch || 0,
                    bearing: newViewState.bearing || 0,
                },
            });
        }
    }, [controlledViewState, enableEvents, setProps]);

    // Click handler
    const handleClick = useCallback((info, event) => {
        if (!isEventEnabled('click', enableEvents) || !setProps) {
            return;
        }
        const normalized = normalizePickInfo(info);
        setProps({
            clickInfo: normalized,
        });
    }, [enableEvents, setProps]);

    // Hover handler
    const handleHover = useCallback((info) => {
        if (!isEventEnabled('hover', enableEvents) || !setProps) {
            return;
        }
        const normalized = normalizePickInfo(info);
        setProps({
            hoverInfo: normalized,
        });
    }, [enableEvents, setProps]);

    // Tooltip rendering
    const getTooltip = useCallback((info) => {
        if (!tooltip || !info.picked || !info.object) {
            return null;
        }
        // Simple tooltip - just show properties
        if (tooltip === true) {
            const properties = info.object.properties || info.object;
            const text = Object.entries(properties)
                .filter(([key, value]) => typeof value !== 'object' && !key.startsWith('_'))
                .map(([key, value]) => `${key}: ${value}`)
                .join('\n');
            return text || null;
        }
        // Custom tooltip config
        if (typeof tooltip === 'object') {
            // Check for layer-specific tooltip config
            const layerId = info.layer?.id;
            let tooltipConfig = null;

            if (tooltip.layers && layerId && tooltip.layers[layerId]) {
                // Layer-specific tooltip
                tooltipConfig = tooltip.layers[layerId];
            } else if (tooltip.default) {
                // Default tooltip config when using layers object
                tooltipConfig = tooltip.default;
            } else if (tooltip.html) {
                // Simple {html: "..."} format (backwards compatible)
                tooltipConfig = tooltip;
            }

            if (tooltipConfig && tooltipConfig.html) {
                let html = tooltipConfig.html;
                // Get properties from both object.properties (GeoJSON) and object directly (aggregation layers)
                const props = info.object.properties || {};
                const directProps = info.object || {};
                const allProps = { ...directProps, ...props };

                for (const [key, value] of Object.entries(allProps)) {
                    if (typeof value !== 'object' && typeof value !== 'function') {
                        html = html.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
                    }
                }
                return { html, style: tooltipConfig.style || {} };
            }
        }
        return null;
    }, [tooltip]);

    // Container style with defaults
    const containerStyle = useMemo(() => ({
        position: 'relative',
        width: '100%',
        height: '400px',
        ...style,
    }), [style]);

    return (
        <div id={id} style={containerStyle}>
            <DeckGLComponent
                viewState={currentViewState}
                onViewStateChange={handleViewStateChange}
                controller={controller !== false ? (controller || true) : false}
                layers={deckLayers}
                onClick={isEventEnabled('click', enableEvents) ? handleClick : undefined}
                onHover={isEventEnabled('hover', enableEvents) ? handleHover : undefined}
                getTooltip={tooltip ? getTooltip : undefined}
                pickingRadius={5}
            />
        </div>
    );
};

/**
 * Normalize a deck.gl picking info object for Dash callbacks
 */
function normalizePickInfo(info) {
    if (!info || !info.picked) {
        return null;
    }
    // Serialize the object first
    const serializedObject = serializeObject(info.object);
    // Extract properties from the serialized object (not the original)
    const properties = serializedObject?.properties || null;

    return {
        picked: true,
        index: typeof info.index === 'number' ? info.index : null,
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
function serializeObject(obj) {
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

DeckGL.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * Array of layer configurations. Each layer should have a '@@type' property
     * specifying the layer type (e.g., 'GeoJsonLayer', 'TileLayer').
     * Supports all deck.gl layer types.
     */
    layers: PropTypes.arrayOf(PropTypes.object),

    /**
     * Initial view state for uncontrolled mode. Sets the initial camera position.
     * Properties: longitude, latitude, zoom, pitch, bearing
     */
    initialViewState: PropTypes.shape({
        longitude: PropTypes.number,
        latitude: PropTypes.number,
        zoom: PropTypes.number,
        pitch: PropTypes.number,
        bearing: PropTypes.number,
    }),

    /**
     * Controlled view state. When provided, the component operates in controlled mode
     * and this prop fully controls the camera position.
     */
    viewState: PropTypes.shape({
        longitude: PropTypes.number,
        latitude: PropTypes.number,
        zoom: PropTypes.number,
        pitch: PropTypes.number,
        bearing: PropTypes.number,
    }),

    /**
     * Enable map interactions. Can be:
     * - true: Enable all default interactions
     * - false: Disable all interactions
     * - object: Fine-grained control (e.g., {dragPan: true, scrollZoom: false})
     */
    controller: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.object,
    ]),

    /**
     * Enable events for Dash callbacks. Events are disabled by default for performance.
     * Can be:
     * - false: No events (default)
     * - true: Enable all events (click, hover, viewStateChange)
     * - array: Enable specific events, e.g., ['click', 'hover']
     */
    enableEvents: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * Tooltip configuration. Can be:
     * - false: No tooltip (default)
     * - true: Show all properties on hover
     * - object: {html: "template with {property}", style: {}}
     */
    tooltip: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.object,
    ]),

    /**
     * CSS styles for the container div.
     * Default height is 400px if not specified.
     */
    style: PropTypes.object,

    /**
     * (Output) Information about the last clicked feature.
     * Updated when click events are enabled.
     */
    clickInfo: PropTypes.object,

    /**
     * (Output) Information about the currently hovered feature.
     * Updated when hover events are enabled.
     */
    hoverInfo: PropTypes.object,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func,
};

export default DeckGL;
