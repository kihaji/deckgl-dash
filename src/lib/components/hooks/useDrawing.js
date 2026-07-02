/**
 * Drawing/editing state for the DeckGL component: feature collection sync,
 * selection, delete handling, cursor, and the editable layer appended on top
 * of the base deck.gl layers. Extracted verbatim from DeckGL.react.js.
 */
import { useState, useEffect, useMemo, useRef } from 'react';
import { createEditableLayer, deleteFeatures, DRAG_DRAW_MODES, ACTIVE_DRAWING_MODES, getCursorForMode } from '../../utils/drawingManager';

const EMPTY_FEATURE_COLLECTION = { type: 'FeatureCollection', features: [] };

export function useDrawing({ deckLayers, drawingConfig, drawingFeatures, setProps }) {
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
    const isDragDrawMode = Boolean(drawingMode && DRAG_DRAW_MODES.has(drawingMode));
    const isActiveDrawingMode = Boolean(drawingMode &&
        (ACTIVE_DRAWING_MODES.has(drawingMode) || drawingMode === 'modify' || drawingMode === 'translate' || drawingMode === 'delete'));

    // Cursor style for drawing modes
    const drawingCursor = drawingMode ? getCursorForMode(drawingMode) : null;

    return { allLayers, drawingCursor, isDragDrawMode, isActiveDrawingMode };
}
