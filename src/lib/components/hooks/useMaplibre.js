/**
 * MapLibre GL JS integration: map + MapboxOverlay lifecycle, basemap style
 * switching, custom sources/mapLayers on style.load, moveend reporting,
 * drawing-mode interaction toggles, overlay layer updates, controlled
 * view-state sync, and MapLibre-native fitBounds. Extracted verbatim from
 * DeckGL.react.js.
 */
import { useEffect, useRef, useState } from 'react';
import { MapboxOverlay } from '@deck.gl/mapbox';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { isEventEnabled } from '../../utils/eventHandler';
import { applyRangeToLayers } from '../../utils/timeFilter';
import { zoomGateKey } from '../../utils/zoomVisibility';
import { debugLog, debugTime, debugTimeEnd } from '../../utils/debug';

export function useMaplibre({
    maplibreConfig,
    currentViewState,
    controlledViewState,
    fitBounds,
    enableEvents,
    tooltip,
    allLayers,
    handleClick,
    handleHover,
    getTooltip,
    setProps,
    overlayRef,
    timeFilterRef,
    headTimeRef,
    isDragDrawMode,
    isActiveDrawingMode,
    zoomGates,
    mapZoomRef,
    setMapZoomGateKey,
}) {
    const mapContainerRef = useRef(null);
    const mapRef = useRef(null);
    const mapViewStateRef = useRef(null);
    // Keep a ref to maplibreConfig so the style.load handler always reads fresh values
    const maplibreConfigRef = useRef(maplibreConfig);
    maplibreConfigRef.current = maplibreConfig;
    const [, setMapStyleLoaded] = useState(false);
    // Fresh gates for the per-frame zoom handler without re-subscribing
    const zoomGatesRef = useRef(zoomGates);
    zoomGatesRef.current = zoomGates;
    const lastGateKeyRef = useRef('');

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
        mapZoomRef.current = map.getZoom();

        // Zoom-gated visibility: the zoom event fires every frame, so only bump
        // React state (which pushes new layers) when a gate's in-range bit flips.
        map.on('zoom', () => {
            mapZoomRef.current = map.getZoom();
            const gates = zoomGatesRef.current;
            if (!gates || gates.length === 0) {
                return;
            }
            const key = zoomGateKey(gates, mapZoomRef.current);
            if (key !== lastGateKeyRef.current) {
                lastGateKeyRef.current = key;
                setMapZoomGateKey(key);
            }
        });

        // Create MapboxOverlay for deck.gl layers
        // Default interleaved to false for better performance (deck.gl renders on top of MapLibre)
        // Set interleaved=true only if you need deck.gl layers below MapLibre labels
        const overlay = new MapboxOverlay({
            interleaved: maplibreConfig.interleaved === true,
            layers: (timeFilterRef.current && headTimeRef.current != null)
                ? applyRangeToLayers(allLayers, headTimeRef.current, timeFilterRef.current)
                : allLayers,
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
        debugLog('useEffect: overlay setProps', { hasOverlay: Boolean(overlayRef.current), layersCount: allLayers?.length });
        if (overlayRef.current) {
            debugTime('[DeckGL] overlay.setProps');
            // Apply the active time-filter window so new base layers render filtered.
            const layersToSet = (timeFilterRef.current && headTimeRef.current != null)
                ? applyRangeToLayers(allLayers, headTimeRef.current, timeFilterRef.current)
                : allLayers;
            overlayRef.current.setProps({
                layers: layersToSet,
                onClick: isEventEnabled('click', enableEvents) ? handleClick : undefined,
                onHover: isEventEnabled('hover', enableEvents) ? handleHover : undefined,
                getTooltip: tooltip ? getTooltip : undefined,
            });
            debugTimeEnd('[DeckGL] overlay.setProps');
        }
    }, [allLayers]);

    // Sync controlled viewState to MapLibre map (for programmatic control)
    useEffect(() => {
        debugLog('useEffect: controlledViewState sync', { hasMap: Boolean(mapRef.current), controlledViewState });
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

    return { mapContainerRef };
}
