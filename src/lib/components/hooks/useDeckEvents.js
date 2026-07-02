/**
 * Dash-facing event handlers: view-state reporting, click/hover pick events,
 * and tooltip rendering. Extracted verbatim from DeckGL.react.js.
 */
import { useCallback } from 'react';
import { isEventEnabled, normalizePickInfo } from '../../utils/eventHandler';

export function useDeckEvents({ controlledViewState, setInternalViewState, enableEvents, tooltip, setProps }) {
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
    }, [controlledViewState, setInternalViewState, enableEvents, setProps]);

    // Click handler
    const handleClick = useCallback((info) => {
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

    return { handleViewStateChange, handleClick, handleHover, getTooltip };
}
