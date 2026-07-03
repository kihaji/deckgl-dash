import React, { useState, useMemo, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { WebMercatorViewport } from '@deck.gl/core';
import { DeckGL as DeckGLComponent } from '@deck.gl/react';
import { createLayers } from '../utils/layerRegistry';
import { isEventEnabled } from '../utils/eventHandler';
import { applyRangeToLayers, resolveHeadTime } from '../utils/timeFilter';
import { applyLayerOrder } from '../utils/layerOrder';
import { extractZoomGates, zoomGateKey, applyZoomVisibility } from '../utils/zoomVisibility';
import { debugLog, debugTime, debugTimeEnd } from '../utils/debug';
import { useDrawing } from './hooks/useDrawing';
import { useTimeFilterAnimation } from './hooks/useTimeFilterAnimation';
import { useMaplibre } from './hooks/useMaplibre';
import { useDeckEvents } from './hooks/useDeckEvents';

/**
 * DeckGL component for Plotly Dash
 * A high-performance WebGL-powered visualization component wrapping deck.gl
 * Supports all deck.gl layer types via JSON configuration
 * Optional MapLibre GL JS integration for basemaps
 *
 * The component is a thin composition layer; the six concerns live in hooks:
 * layer building (below), drawing (useDrawing), time-filter animation
 * (useTimeFilterAnimation), MapLibre integration (useMaplibre), and Dash
 * event/tooltip handlers (useDeckEvents).
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
    timeFilter = null,
    setProps,
}) => {
    debugLog('RENDER', { id, layersCount: layers?.length, hasMaplibreConfig: Boolean(maplibreConfig), controlledViewState });

    // Shared renderer handles: the MapLibre overlay (set by useMaplibre) and the
    // deck-only <DeckGL> instance — the animation engine writes to whichever is live.
    const overlayRef = useRef(null);
    const deckRef = useRef(null);
    // Ref to the deck-only container div (used to read pixel dimensions for fitBounds)
    const containerRef = useRef(null);

    // Internal view state for uncontrolled mode
    const [internalViewState, setInternalViewState] = useState(initialViewState);

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

    // Create deck.gl layers from JSON configs, merging per-layer data overrides.
    // visibleMinZoom/visibleMaxZoom gating keys are extracted here (zoomGates) and
    // stripped before layer creation.
    const layerOptions = useMemo(() => ({ setProps, enableEvents }), [setProps, enableEvents]);
    const { deckLayers, zoomGates } = useMemo(() => {
        // Merge incoming layerData into the accumulated ref before reading it
        if (layerData && Object.keys(layerData).length > 0) {
            accumulatedLayerDataRef.current = { ...accumulatedLayerDataRef.current, ...layerData };
        }
        const baseConfigs = layers || [];
        const mergedData = accumulatedLayerDataRef.current;
        debugLog('useMemo: createLayers called', { layersCount: baseConfigs.length, hasLayerData: Object.keys(mergedData).length > 0 });
        debugTime('[DeckGL] createLayers');
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
        const { configs: gatedConfigs, gates } = extractZoomGates(mergedConfigs);
        const result = createLayers(gatedConfigs, layerOptions);
        debugTimeEnd('[DeckGL] createLayers');
        return { deckLayers: result, zoomGates: gates };
    }, [layers, layerData, layerOrder, layerOptions]);

    // Drawing: feature state, delete handling, cursor, editable layer on top
    const { allLayers, drawingCursor, isDragDrawMode, isActiveDrawingMode } = useDrawing({
        deckLayers, drawingConfig, drawingFeatures, setProps,
    });

    // Zoom-gated visibility: fold visibleMinZoom/visibleMaxZoom into `visible`.
    // MapLibre owns its camera, so its zoom lives in a ref; a state key bumps a
    // re-render only when some gate actually flips (the zoom event is per-frame).
    const mapZoomRef = useRef(null);
    const [mapZoomGateKey, setMapZoomGateKey] = useState('');
    const gateZoom = maplibreConfig ? mapZoomRef.current : currentViewState.zoom;
    const gateKey = maplibreConfig ? mapZoomGateKey : zoomGateKey(zoomGates, currentViewState.zoom);
    const gatedLayers = useMemo(
        () => (gateZoom == null ? allLayers : applyZoomVisibility(allLayers, zoomGates, gateZoom)),
        [allLayers, zoomGates, gateKey]  // gateKey is the memo trigger; gateZoom is read fresh
    );

    // Time-filter animation engine (rAF loop driving GPU filterRange updates)
    const { timeFilterRef, headTimeRef } = useTimeFilterAnimation({
        timeFilter, allLayers: gatedLayers, overlayRef, deckRef, setProps,
    });

    // Dash-facing event handlers and tooltip renderer
    const { handleViewStateChange, handleClick, handleHover, getTooltip } = useDeckEvents({
        controlledViewState, setInternalViewState, enableEvents, tooltip, setProps,
    });

    // MapLibre map + overlay lifecycle (no-op while maplibreConfig is null)
    const { mapContainerRef } = useMaplibre({
        maplibreConfig, currentViewState, controlledViewState, fitBounds, enableEvents, tooltip,
        allLayers: gatedLayers, handleClick, handleHover, getTooltip, setProps,
        overlayRef, timeFilterRef, headTimeRef, isDragDrawMode, isActiveDrawingMode,
        zoomGates, mapZoomRef, setMapZoomGateKey,
    });

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

    // Deck-only mode: compute effective controller with drawing overrides.
    // Must stay above the MapLibre early return — hooks may not run conditionally.
    const effectiveController = useMemo(() => {
        if (controller === false) return false;
        const base = typeof controller === 'object' ? controller : {};
        if (isActiveDrawingMode) {
            return { ...base, doubleClickZoom: false, ...(isDragDrawMode ? { dragPan: false } : {}) };
        }
        return controller || true;
    }, [controller, isActiveDrawingMode, isDragDrawMode]);

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

    // Apply the time-filter window to the rendered layers (cheap clone of target layers
    // only) so React re-renders stay consistent with the rAF loop's imperative updates.
    const renderedLayers = timeFilter
        ? applyRangeToLayers(gatedLayers, resolveHeadTime(timeFilter, headTimeRef.current), timeFilter)
        : gatedLayers;

    return (
        <div ref={containerRef} id={id} style={{ ...containerStyle, ...(drawingCursor ? { cursor: drawingCursor } : {}) }}>
            <DeckGLComponent
                ref={deckRef}
                viewState={currentViewState}
                onViewStateChange={handleViewStateChange}
                controller={effectiveController}
                layers={renderedLayers}
                onClick={isEventEnabled('click', enableEvents) ? handleClick : undefined}
                onHover={isEventEnabled('hover', enableEvents) ? handleHover : undefined}
                getTooltip={tooltip ? getTooltip : undefined}
                pickingRadius={5}
                getCursor={() => drawingCursor || 'grab'}
            />
        </div>
    );
};

DeckGL.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * Array of layer configurations. Each layer should have a '@@type' property
     * specifying the layer type (e.g., 'GeoJsonLayer', 'TileLayer').
     * Supports all deck.gl layer types.
     *
     * Per-layer `visibleMinZoom`/`visibleMaxZoom` keys gate the layer's visibility
     * by the current map zoom (LOD-style dashboards) in both render modes; the
     * user-supplied `visible` is preserved and re-applied when back in range.
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
     * - interleaved: bool - Enable deck.gl layer interleaving (default: false; deck.gl renders on top of MapLibre)
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
     *   'draw_rectangle', 'draw_square', 'draw_point', 'view', 'modify', 'translate', 'delete')
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
     * Time-filter animation config. Drives an internal requestAnimationFrame loop that
     * sets each filterable layer's `filterRange` on the GPU (via DataFilterExtension) to a
     * sliding window `[current - window, current]`. Filtering happens client-side at 60fps
     * with no per-frame server round trips; only the throttled `currentTime` is reported back.
     *
     * Target layers are those carrying a DataFilterExtension (declare `get_filter_value` in
     * Python), or an explicit `layerIds` allowlist. All time values must share one scale —
     * keep them float32-safe (e.g. seconds since `domain[0]`).
     *
     * Shape:
     * - domain: [tMin, tMax] - full time extent (required for playback)
     * - window: number - sliding-window width in time units
     * - current: number - head time T; authoritative while paused (slider scrubbing)
     * - playing: bool - run the animation loop
     * - speed: number - time units advanced per wall-clock second (default: full sweep in ~20s)
     * - loop: bool - wrap the head back to `domain[0]+window` at the end (default true)
     * - softEdge: number - optional fade width mapped to `filterSoftRange`
     * - layerIds: string[] - explicit target layer IDs (default: auto-detect)
     * - nonce: number - bump to force a re-sync of an unchanged `current`
     */
    timeFilter: PropTypes.shape({
        domain: PropTypes.arrayOf(PropTypes.number),
        window: PropTypes.number,
        current: PropTypes.number,
        playing: PropTypes.bool,
        speed: PropTypes.number,
        loop: PropTypes.bool,
        softEdge: PropTypes.number,
        layerIds: PropTypes.arrayOf(PropTypes.string),
        nonce: PropTypes.number,
    }),

    /**
     * (Output) The current playback head time T during animation, reported ~8 Hz.
     * Use it to drive a slider handle, a time readout, or other callbacks.
     */
    currentTime: PropTypes.number,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func,
};

export default DeckGL;
