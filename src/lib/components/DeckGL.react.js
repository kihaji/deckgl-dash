import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { WebMercatorViewport } from '@deck.gl/core';
import { DeckGL as DeckGLComponent } from '@deck.gl/react';
import { MapboxOverlay } from '@deck.gl/mapbox';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { createLayers } from '../utils/layerRegistry';
import { isEventEnabled } from '../utils/eventHandler';
import { createEditableLayer, deleteFeatures, DRAG_DRAW_MODES, ACTIVE_DRAWING_MODES, getCursorForMode } from '../utils/drawingManager';

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

/**
 * Reorder layer configs according to a list of layer IDs (bottom to top).
 * Layers not mentioned in the order array are appended at the top.
 */
function applyLayerOrder(configs, order) {
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

const EMPTY_FEATURE_COLLECTION = { type: 'FeatureCollection', features: [] };

const DeckGL = ({
    id,
    layers = [],
    layerData,
    layerOrder,
    initialViewState = DEFAULT_VIEW_STATE,
    viewState: controlledViewState,
    fitBounds = null,
    controller = true,
    enableEvents = false,
    tooltip = false,
    style = {},
    maplibreConfig = null,
    drawingConfig = null,
    drawingFeatures = null,
    drawingEvent = null,
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
    // Ref to the deck-only container div (used to read pixel dimensions for fitBounds)
    const containerRef = useRef(null);
    const overlayRef = useRef(null);
    const mapViewStateRef = useRef(null);
    // Keep a ref to maplibreConfig so the style.load handler always reads fresh values
    const maplibreConfigRef = useRef(maplibreConfig);
    maplibreConfigRef.current = maplibreConfig;

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

    // Accumulate layerData entries so each callback only sends its own layer's data.
    // Merge happens inside useMemo (not useEffect) so the current render sees the update immediately.
    const accumulatedLayerDataRef = useRef({});

    // Create deck.gl layers from JSON configs, merging per-layer data overrides
    const layerOptions = useMemo(() => ({ setProps, enableEvents }), [setProps, enableEvents]);
    const deckLayers = useMemo(() => {
        // Merge incoming layerData into the accumulated ref before reading it
        if (layerData && Object.keys(layerData).length > 0) {
            accumulatedLayerDataRef.current = { ...accumulatedLayerDataRef.current, ...layerData };
        }
        const baseConfigs = layers || [];
        const mergedData = accumulatedLayerDataRef.current;
        debugLog('useMemo: createLayers called', { layersCount: baseConfigs.length, hasLayerData: Object.keys(mergedData).length > 0 });
        console.time('[DeckGL] createLayers');
        let mergedConfigs = baseConfigs;
        if (Object.keys(mergedData).length > 0) {
            mergedConfigs = baseConfigs.map(config => {
                const lid = config.id;
                if (lid && lid in mergedData) {
                    return { ...config, data: mergedData[lid] };
                }
                return config;
            });
        }
        if (layerOrder && Array.isArray(layerOrder) && layerOrder.length > 0) {
            mergedConfigs = applyLayerOrder(mergedConfigs, layerOrder);
        }
        const result = createLayers(mergedConfigs, layerOptions);
        console.timeEnd('[DeckGL] createLayers');
        return result;
    }, [layers, layerData, layerOrder, layerOptions]);

    // ===========================================
    // Drawing state
    // ===========================================
    const [internalFeatures, setInternalFeatures] = useState(
        drawingFeatures || EMPTY_FEATURE_COLLECTION
    );
    const [selectedFeatureIndexes, setSelectedFeatureIndexes] = useState([]);

    // Sync external drawingFeatures prop into internal state (e.g., Python clears or sets features)
    const prevDrawingFeaturesRef = useRef(drawingFeatures);
    useEffect(() => {
        if (drawingFeatures !== prevDrawingFeaturesRef.current) {
            prevDrawingFeaturesRef.current = drawingFeatures;
            setInternalFeatures(drawingFeatures || EMPTY_FEATURE_COLLECTION);
            setSelectedFeatureIndexes([]);
        }
    }, [drawingFeatures]);

    // Clear selection when switching modes
    const prevModeRef = useRef(drawingConfig?.mode);
    useEffect(() => {
        if (drawingConfig?.mode !== prevModeRef.current) {
            prevModeRef.current = drawingConfig?.mode;
            setSelectedFeatureIndexes([]);
        }
    }, [drawingConfig?.mode]);

    // Handle delete: when drawingConfig.deleteSelected is set and we have a selection
    useEffect(() => {
        if (drawingConfig?.deleteSelected && selectedFeatureIndexes.length > 0) {
            const updated = deleteFeatures(internalFeatures, selectedFeatureIndexes);
            setInternalFeatures(updated);
            setSelectedFeatureIndexes([]);
            if (setProps) {
                setProps({
                    drawingFeatures: updated,
                    drawingEvent: {
                        type: 'deleteFeature',
                        featureCount: updated.features.length,
                        timestamp: Date.now(),
                    },
                    // Reset deleteSelected flag so it can be triggered again
                    drawingConfig: { ...drawingConfig, deleteSelected: false },
                });
            }
        }
    }, [drawingConfig?.deleteSelected]);

    // Build final layers list: base layers + optional editable drawing layer on top
    const allLayers = useMemo(() => {
        if (!drawingConfig || !drawingConfig.mode || drawingConfig.mode === 'view') {
            return deckLayers;
        }
        const editableLayer = createEditableLayer(
            drawingConfig,
            internalFeatures,
            selectedFeatureIndexes,
            setInternalFeatures,
            setSelectedFeatureIndexes,
            setProps
        );
        return editableLayer ? [...deckLayers, editableLayer] : deckLayers;
    }, [deckLayers, drawingConfig, internalFeatures, selectedFeatureIndexes, setProps]);

    // Determine drawing mode state for controller/cursor adjustments
    const drawingMode = drawingConfig?.mode || null;
    const isDragDrawMode = drawingMode && DRAG_DRAW_MODES.has(drawingMode);
    const isActiveDrawingMode = drawingMode && (ACTIVE_DRAWING_MODES.has(drawingMode) || drawingMode === 'modify' || drawingMode === 'translate');

    // Cursor style for drawing modes
    const drawingCursor = drawingMode ? getCursorForMode(drawingMode) : null;

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

    // Initialize MapLibre map on first mount, or switch style on existing map
    useEffect(() => {
        if (!maplibreConfig || !mapContainerRef.current) {
            return;
        }

        const newStyle = maplibreConfig.style || { version: 8, sources: {}, layers: [] };

        // Style change on existing map — use setStyle() to preserve map + overlay
        if (mapRef.current) {
            debugLog('setStyle: switching basemap style');
            setMapStyleLoaded(false);
            if (setProps) {
                setProps({ mapStyleLoaded: false });
            }
            mapRef.current.setStyle(newStyle);
            return; // no cleanup — map stays alive
        }

        // First mount — create map and overlay from scratch
        const effectiveViewState = mapViewStateRef.current || currentViewState;
        const mapOptions = {
            container: mapContainerRef.current,
            style: newStyle,
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
            layers: allLayers,
            onClick: isEventEnabled('click', enableEvents) ? handleClick : undefined,
            onHover: isEventEnabled('hover', enableEvents) ? handleHover : undefined,
            getTooltip: tooltip ? getTooltip : undefined,
        });
        overlayRef.current = overlay;

        // Add overlay as map control
        map.addControl(overlay);

        // Handle style load — reads maplibreConfigRef to get latest sources/layers
        map.on('style.load', () => {
            setMapStyleLoaded(true);
            if (setProps) {
                setProps({ mapStyleLoaded: true });
            }

            const cfg = maplibreConfigRef.current;

            // Add custom sources
            if (cfg?.sources) {
                for (const [sourceId, sourceSpec] of Object.entries(cfg.sources)) {
                    if (!map.getSource(sourceId)) {
                        map.addSource(sourceId, sourceSpec);
                    }
                }
            }

            // Add custom map layers
            if (cfg?.mapLayers) {
                for (const layerSpec of cfg.mapLayers) {
                    if (!map.getLayer(layerSpec.id)) {
                        map.addLayer(layerSpec);
                    }
                }
            }
        });

        // Fire Dash callback on moveend (not move) to avoid excessive updates
        // MapLibre handles its own view state — we only report to Dash when movement ends
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

        // No cleanup — unmount is handled by a separate effect
    }, [maplibreConfig?.style]); // Re-run only when style changes

    // Cleanup on unmount only — never on style changes
    useEffect(() => {
        return () => {
            if (overlayRef.current) {
                overlayRef.current.finalize();
                overlayRef.current = null;
            }
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, []);

    // Disable map interactions that conflict with drawing modes
    useEffect(() => {
        if (!mapRef.current) return;
        // Disable double-click zoom in any active drawing/editing mode
        if (isActiveDrawingMode) {
            mapRef.current.doubleClickZoom.disable();
        } else {
            mapRef.current.doubleClickZoom.enable();
        }
        // Disable drag panning for drag-draw modes (circle, rectangle, square)
        if (isDragDrawMode) {
            mapRef.current.dragPan.disable();
        } else {
            mapRef.current.dragPan.enable();
        }
    }, [isDragDrawMode, isActiveDrawingMode]);

    // Update overlay layers when deck.gl layers change
    // Note: We intentionally exclude callback functions from deps - they use refs internally
    useEffect(() => {
        debugLog('useEffect: overlay setProps', { hasOverlay: !!overlayRef.current, layersCount: deckLayers?.length });
        if (overlayRef.current) {
            console.time('[DeckGL] overlay.setProps');
            overlayRef.current.setProps({
                layers: allLayers,
                onClick: isEventEnabled('click', enableEvents) ? handleClick : undefined,
                onHover: isEventEnabled('hover', enableEvents) ? handleHover : undefined,
                getTooltip: tooltip ? getTooltip : undefined,
            });
            console.timeEnd('[DeckGL] overlay.setProps');
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [allLayers]);

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

    // Fit the camera to a bounding box. `fitBounds` shape:
    //   { bounds: [[west, south], [east, north]], padding?: number, maxZoom?: number }
    // MapLibre mode uses the map's native, viewport-aware fitBounds.
    useEffect(() => {
        if (!fitBounds || !Array.isArray(fitBounds.bounds) || !mapRef.current) {
            return;
        }
        const [[west, south], [east, north]] = fitBounds.bounds;
        const padding = fitBounds.padding ?? 20;
        const maxZoom = fitBounds.maxZoom ?? 20;
        // Guard the moveend handler against firing a Dash viewState callback for this programmatic move.
        isUpdatingViewRef.current = true;
        try {
            mapRef.current.fitBounds([[west, south], [east, north]], { padding, maxZoom, duration: 0 });
        } catch (e) {
            console.warn('fitBounds (MapLibre) failed:', e);
        }
    }, [fitBounds]);

    // Deck-only mode: compute a fitted view state with WebMercatorViewport using the
    // container's real pixel size, then drive the uncontrolled camera.
    useEffect(() => {
        if (!fitBounds || !Array.isArray(fitBounds.bounds) || maplibreConfig) {
            return;
        }
        const el = containerRef.current;
        if (!el || !el.clientWidth || !el.clientHeight) {
            return;
        }
        const width = el.clientWidth;
        const height = el.clientHeight;
        const [[west, south], [east, north]] = fitBounds.bounds;
        const padding = fitBounds.padding ?? 20;
        const maxZoom = fitBounds.maxZoom ?? 20;
        setInternalViewState(prev => {
            try {
                // Degenerate bounds (single point / zero span): fall back to a sane zoom.
                if (west === east && south === north) {
                    return { ...prev, longitude: west, latitude: south, zoom: Math.min(maxZoom, 15) };
                }
                const vp = new WebMercatorViewport({
                    width, height,
                    longitude: prev.longitude, latitude: prev.latitude, zoom: prev.zoom,
                });
                const fitted = vp.fitBounds([[west, south], [east, north]], { padding });
                return { ...prev, longitude: fitted.longitude, latitude: fitted.latitude, zoom: Math.min(fitted.zoom, maxZoom) };
            } catch (e) {
                console.warn('fitBounds (deck-only) failed:', e);
                return prev;
            }
        });
    }, [fitBounds]);

    // ===========================================
    // Render
    // ===========================================

    // MapLibre mode - render map container
    if (maplibreConfig) {
        return (
            <div id={id} style={containerStyle}>
                <div
                    ref={mapContainerRef}
                    style={{
                        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                        ...(drawingCursor ? { cursor: drawingCursor } : {}),
                    }}
                />
            </div>
        );
    }

    // Standard deck.gl-only mode — compute effective controller with drawing overrides
    const effectiveController = useMemo(() => {
        if (controller === false) return false;
        const base = typeof controller === 'object' ? controller : {};
        if (isActiveDrawingMode) {
            return { ...base, doubleClickZoom: false, ...(isDragDrawMode ? { dragPan: false } : {}) };
        }
        return controller || true;
    }, [controller, isActiveDrawingMode, isDragDrawMode]);

    return (
        <div ref={containerRef} id={id} style={{ ...containerStyle, ...(drawingCursor ? { cursor: drawingCursor } : {}) }}>
            <DeckGLComponent
                viewState={currentViewState}
                onViewStateChange={handleViewStateChange}
                controller={effectiveController}
                layers={allLayers}
                onClick={isEventEnabled('click', enableEvents) ? handleClick : undefined}
                onHover={isEventEnabled('hover', enableEvents) ? handleHover : undefined}
                getTooltip={tooltip ? getTooltip : undefined}
                pickingRadius={5}
                getCursor={() => drawingCursor || 'grab'}
            />
        </div>
    );
};

/**
 * Normalize a deck.gl picking info object for Dash callbacks
 */
function normalizePickInfo(info) {
    if (!info) {
        return null;
    }
    const picked = !!info.picked;
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
     * Per-layer data overrides. Dict mapping layer IDs to data values.
     * Merges with the `layers` prop — only the `data` field of matching layers is replaced.
     * Allows updating individual layer data without resending the entire layers array.
     */
    layerData: PropTypes.objectOf(PropTypes.any),

    /**
     * Layer rendering order as an array of layer IDs from bottom to top.
     * When provided, layers are reordered to match this sequence without
     * resending layer data. Layers not listed are appended at the top.
     * Set to an empty array or null to use the original layers array order.
     */
    layerOrder: PropTypes.arrayOf(PropTypes.string),

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
     * Fit the camera to a geographic bounding box. Setting this prop drives the real
     * camera: MapLibre mode uses the map's native `fitBounds`; deck-only mode uses
     * `WebMercatorViewport.fitBounds` with the container's real pixel size. Both are
     * viewport-aware, so the result frames the bounds tightly.
     *
     * Shape:
     * - bounds: [[west, south], [east, north]] - the box to fit (required)
     * - padding: number - pixels of padding around the bounds (default 20)
     * - maxZoom: number - clamp the fitted zoom (default 20)
     */
    fitBounds: PropTypes.shape({
        bounds: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
        padding: PropTypes.number,
        maxZoom: PropTypes.number,
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
     * (Output) Information about the last successful remote data load.
     * Updated when 'dataLoad' is included in enableEvents and a layer loads data from a URL.
     * Contains: { layerId, featureCount, timestamp }
     */
    dataLoadInfo: PropTypes.object,

    /**
     * (Output) Information about the last data load error.
     * Updated when 'dataLoadError' is included in enableEvents and a layer fails to load data from a URL.
     * Contains: { layerId, error, timestamp }
     */
    dataLoadError: PropTypes.object,

    /**
     * Drawing/editing configuration. When provided with a drawing mode,
     * an EditableGeoJsonLayer is added on top of all other layers.
     *
     * Shape:
     * - mode: string - Drawing mode ('draw_line', 'draw_polygon', 'draw_circle',
     *   'draw_rectangle', 'draw_square', 'draw_point', 'view', 'modify', 'translate')
     * - selectedFeatureIndexes: number[] - Indexes of features selected for editing
     * - style: object - Style overrides for the editable layer
     *   - fillColor: [r,g,b,a] - Fill color for drawn features
     *   - lineColor: [r,g,b,a] - Line/stroke color
     *   - lineWidth: number - Line width in pixels
     *   - tentativeFillColor: [r,g,b,a] - Fill color while drawing
     *   - tentativeLineColor: [r,g,b,a] - Line color while drawing
     *   - editHandlePointColor: [r,g,b,a] - Color of vertex edit handles
     */
    drawingConfig: PropTypes.shape({
        mode: PropTypes.string,
        selectedFeatureIndexes: PropTypes.arrayOf(PropTypes.number),
        style: PropTypes.object,
        deleteSelected: PropTypes.bool,
    }),

    /**
     * (Input/Output) GeoJSON FeatureCollection of drawn/edited features.
     * Can be set from Python to pre-populate features, and is updated
     * from JS when features are added/modified.
     */
    drawingFeatures: PropTypes.object,

    /**
     * (Output) Information about the last drawing event.
     * Contains: { type, featureCount, timestamp }
     */
    drawingEvent: PropTypes.object,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func,
};

export default DeckGL;
