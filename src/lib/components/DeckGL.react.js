import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { DeckGL as DeckGLComponent } from '@deck.gl/react';
import { MapboxOverlay } from '@deck.gl/mapbox';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { createLayers } from '../utils/layerRegistry';
import { isEventEnabled } from '../utils/eventHandler';

/**
 * DeckGL component for Plotly Dash
 * A high-performance WebGL-powered visualization component wrapping deck.gl
 * Supports all deck.gl layer types via JSON configuration
 * Optional MapLibre GL JS integration for basemaps
 */
const DEFAULT_VIEW_STATE = {
    longitude: -122.4,
    latitude: 37.8,
    zoom: 11,
    pitch: 0,
    bearing: 0,
};

// Debug flag - set to true to enable performance logging
const DEBUG_PERF = false;
const debugLog = DEBUG_PERF ? (...args) => console.log('[DeckGL]', ...args) : () => {};

const DeckGL = ({
    id,
    layers = [],
    initialViewState = DEFAULT_VIEW_STATE,
    viewState: controlledViewState,
    controller = true,
    enableEvents = false,
    tooltip = false,
    style = {},
    maplibreConfig = null,
    setProps,
}) => {
    // Track if layers reference changed
    const prevLayersRef = useRef(layers);
    const layersChanged = prevLayersRef.current !== layers;
    prevLayersRef.current = layers;

    debugLog('RENDER', { id, layersCount: layers?.length, hasMaplibreConfig: !!maplibreConfig, controlledViewState, layersChanged });
    // Refs for MapLibre mode
    const mapContainerRef = useRef(null);
    const mapRef = useRef(null);
    const overlayRef = useRef(null);
    const mapViewStateRef = useRef(null);

    // Internal view state for uncontrolled mode
    const [internalViewState, setInternalViewState] = useState(initialViewState);
    const [mapStyleLoaded, setMapStyleLoaded] = useState(false);

    // Use controlled view state if provided, otherwise use internal
    const currentViewState = controlledViewState || internalViewState;

    // Update internal view state when initialViewState changes (uncontrolled mode)
    useEffect(() => {
        debugLog('useEffect: initialViewState', { controlledViewState, initialViewState });
        if (!controlledViewState && initialViewState) {
            setInternalViewState(initialViewState);
        }
    }, [initialViewState, controlledViewState]);

    // Create deck.gl layers from JSON configs
    const deckLayers = useMemo(() => {
        debugLog('useMemo: createLayers called', { layersCount: layers?.length });
        console.time('[DeckGL] createLayers');
        const result = createLayers(layers || []);
        console.timeEnd('[DeckGL] createLayers');
        return result;
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
    const containerStyle = useMemo(() => {
        debugLog('useMemo: containerStyle');
        return {
            position: 'relative',
            width: '100%',
            height: '400px',
            ...style,
        };
    }, [style]);

    // ===========================================
    // MapLibre GL JS Integration
    // ===========================================

    // Ref to track if view change originated from programmatic update (to avoid feedback loops)
    const isUpdatingViewRef = useRef(false);

    // Initialize MapLibre map when maplibreConfig is provided
    useEffect(() => {
        if (!maplibreConfig || !mapContainerRef.current) {
            return;
        }

        // Create MapLibre map — prefer saved view state (from prior style) over initial
        const effectiveViewState = mapViewStateRef.current || currentViewState;
        const mapOptions = {
            container: mapContainerRef.current,
            style: maplibreConfig.style || { version: 8, sources: {}, layers: [] },
            center: [effectiveViewState.longitude, effectiveViewState.latitude],
            zoom: effectiveViewState.zoom,
            pitch: effectiveViewState.pitch || 0,
            bearing: effectiveViewState.bearing || 0,
            attributionControl: maplibreConfig.attributionControl !== false,
            ...(maplibreConfig.mapOptions || {}),
        };

        const map = new maplibregl.Map(mapOptions);
        mapRef.current = map;

        // Create MapboxOverlay for deck.gl layers
        // Default interleaved to false for better performance (deck.gl renders on top of MapLibre)
        // Set interleaved=true only if you need deck.gl layers below MapLibre labels
        const overlay = new MapboxOverlay({
            interleaved: maplibreConfig.interleaved === true,
            layers: deckLayers,
            onClick: isEventEnabled('click', enableEvents) ? handleClick : undefined,
            onHover: isEventEnabled('hover', enableEvents) ? handleHover : undefined,
            getTooltip: tooltip ? getTooltip : undefined,
        });
        overlayRef.current = overlay;

        // Add overlay as map control
        map.addControl(overlay);

        // Handle style load - add custom sources and layers
        map.on('style.load', () => {
            setMapStyleLoaded(true);
            if (setProps) {
                setProps({ mapStyleLoaded: true });
            }

            // Add custom sources
            if (maplibreConfig.sources) {
                for (const [sourceId, sourceSpec] of Object.entries(maplibreConfig.sources)) {
                    if (!map.getSource(sourceId)) {
                        map.addSource(sourceId, sourceSpec);
                    }
                }
            }

            // Add custom map layers
            if (maplibreConfig.mapLayers) {
                for (const layerSpec of maplibreConfig.mapLayers) {
                    if (!map.getLayer(layerSpec.id)) {
                        map.addLayer(layerSpec);
                    }
                }
            }
        });

        // Fire Dash callback on moveend (not move) to avoid excessive updates
        // MapLibre handles its own view state - we only report to Dash when movement ends
        map.on('moveend', () => {
            debugLog('map.moveend event', { isUpdating: isUpdatingViewRef.current, enableEvents });
            // Always capture the current camera position so it survives style changes
            const center = map.getCenter();
            mapViewStateRef.current = {
                longitude: center.lng,
                latitude: center.lat,
                zoom: map.getZoom(),
                pitch: map.getPitch(),
                bearing: map.getBearing(),
            };

            // Skip Dash callback if this was triggered by programmatic update
            if (isUpdatingViewRef.current) {
                isUpdatingViewRef.current = false;
                return;
            }

            // Fire Dash callback if viewStateChange events are enabled
            if (isEventEnabled('viewStateChange', enableEvents) && setProps) {
                debugLog('map.moveend: calling setProps');
                setProps({ viewState: mapViewStateRef.current });
            }
        });

        // Cleanup on unmount or style change
        return () => {
            // Snapshot the camera position before destroying the map
            if (mapRef.current) {
                const center = mapRef.current.getCenter();
                mapViewStateRef.current = {
                    longitude: center.lng,
                    latitude: center.lat,
                    zoom: mapRef.current.getZoom(),
                    pitch: mapRef.current.getPitch(),
                    bearing: mapRef.current.getBearing(),
                };
            }
            if (overlayRef.current) {
                overlayRef.current.finalize();
                overlayRef.current = null;
            }
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
            setMapStyleLoaded(false);
        };
    }, [maplibreConfig?.style]); // Re-initialize only when style changes

    // Update overlay layers when deck.gl layers change
    // Note: We intentionally exclude callback functions from deps - they use refs internally
    useEffect(() => {
        debugLog('useEffect: overlay setProps', { hasOverlay: !!overlayRef.current, layersCount: deckLayers?.length });
        if (overlayRef.current) {
            console.time('[DeckGL] overlay.setProps');
            overlayRef.current.setProps({
                layers: deckLayers,
                onClick: isEventEnabled('click', enableEvents) ? handleClick : undefined,
                onHover: isEventEnabled('hover', enableEvents) ? handleHover : undefined,
                getTooltip: tooltip ? getTooltip : undefined,
            });
            console.timeEnd('[DeckGL] overlay.setProps');
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [deckLayers]);

    // Sync controlled viewState to MapLibre map (for programmatic control)
    useEffect(() => {
        debugLog('useEffect: controlledViewState sync', { hasMap: !!mapRef.current, controlledViewState });
        if (mapRef.current && controlledViewState) {
            isUpdatingViewRef.current = true;
            mapRef.current.jumpTo({
                center: [controlledViewState.longitude, controlledViewState.latitude],
                zoom: controlledViewState.zoom,
                pitch: controlledViewState.pitch || 0,
                bearing: controlledViewState.bearing || 0,
            });
        }
    }, [controlledViewState]);

    // ===========================================
    // Render
    // ===========================================

    // MapLibre mode - render map container
    if (maplibreConfig) {
        return (
            <div id={id} style={containerStyle}>
                <div
                    ref={mapContainerRef}
                    style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}
                />
            </div>
        );
    }

    // Standard deck.gl-only mode (backward compatible)
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
     * MapLibre GL JS configuration. When provided, renders MapLibre as the base map
     * with deck.gl layers as overlays via MapboxOverlay.
     *
     * Shape:
     * - style: string | object - Style URL or inline MapLibre style spec (required)
     * - sources: object - Additional sources {id: sourceSpec}
     * - mapLayers: array - Additional MapLibre layers
     * - interleaved: bool - Enable deck.gl layer interleaving (default: true)
     * - attributionControl: bool - Show attribution control (default: true)
     * - mapOptions: object - Additional MapLibre Map options
     */
    maplibreConfig: PropTypes.shape({
        style: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
        sources: PropTypes.object,
        mapLayers: PropTypes.arrayOf(PropTypes.object),
        interleaved: PropTypes.bool,
        attributionControl: PropTypes.bool,
        mapOptions: PropTypes.object,
    }),

    /**
     * (Output) Indicates when the MapLibre style has finished loading.
     * Useful for knowing when custom sources/layers can be added.
     */
    mapStyleLoaded: PropTypes.bool,

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
