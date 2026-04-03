/**
 * Drawing Manager - Creates and manages EditableGeoJsonLayer for interactive drawing
 * Uses @deck.gl-community/editable-layers (successor to nebula.gl)
 */

import {
    EditableGeoJsonLayer,
    ViewMode,
    ModifyMode,
    TranslateMode,
    DrawPointMode,
    DrawLineStringMode,
    DrawPolygonMode,
    DrawRectangleMode,
    DrawSquareMode,
    DrawCircleFromCenterMode,
} from '@deck.gl-community/editable-layers';

/**
 * Map of user-facing mode strings to editable-layers mode class instances
 */
const MODE_MAP = {
    view: new ViewMode(),
    modify: new ModifyMode(),
    translate: new TranslateMode(),
    draw_point: new DrawPointMode(),
    draw_line: new DrawLineStringMode(),
    draw_polygon: new DrawPolygonMode(),
    draw_rectangle: new DrawRectangleMode(),
    draw_square: new DrawSquareMode(),
    draw_circle: new DrawCircleFromCenterMode(),
};

/** Drawing modes that use drag interaction (conflict with map panning) */
export const DRAG_DRAW_MODES = new Set(['draw_circle', 'draw_rectangle', 'draw_square']);

/** All active drawing modes (not view) — used for cursor and doubleClickZoom */
export const ACTIVE_DRAWING_MODES = new Set([
    'draw_point', 'draw_line', 'draw_polygon',
    'draw_rectangle', 'draw_square', 'draw_circle',
]);

/** Modes where clicking a feature should select it */
const SELECTION_MODES = new Set(['modify', 'translate']);

/** Events that should sync completed state to Python */
const SYNC_EVENTS = new Set(['addFeature', 'finishMovePosition', 'removePosition', 'addPosition']);

/**
 * Get the mode instance for a mode string
 * @param {string} modeStr - Mode string (e.g., 'draw_polygon')
 * @returns {object|null} Mode instance or null
 */
export function getModeInstance(modeStr) {
    return MODE_MAP[modeStr] || null;
}

/**
 * Default style values for the editable layer
 */
const DEFAULT_STYLE = {
    fillColor: [255, 140, 0, 100],
    lineColor: [0, 0, 0, 255],
    lineWidth: 2,
    tentativeFillColor: [255, 140, 0, 50],
    tentativeLineColor: [255, 140, 0, 200],
    editHandlePointColor: [255, 0, 0, 255],
    selectedFillColor: [255, 200, 0, 150],
    selectedLineColor: [255, 100, 0, 255],
    pointRadius: 5,
};

/**
 * CSS cursor for each drawing mode
 */
export function getCursorForMode(modeStr) {
    if (ACTIVE_DRAWING_MODES.has(modeStr)) return 'crosshair';
    if (SELECTION_MODES.has(modeStr)) return 'pointer';
    return 'grab';
}

/**
 * Create an EditableGeoJsonLayer for drawing/editing
 * @param {object} drawingConfig - Drawing configuration { mode, selectedFeatureIndexes, style }
 * @param {object} features - Current GeoJSON FeatureCollection
 * @param {number[]} selectedIndexes - Currently selected feature indexes
 * @param {function} setFeatures - React state setter for features
 * @param {function} setSelectedIndexes - React state setter for selected indexes
 * @param {function} setProps - Dash callback function
 * @returns {EditableGeoJsonLayer|null} Layer instance or null if mode is invalid
 */
export function createEditableLayer(drawingConfig, features, selectedIndexes, setFeatures, setSelectedIndexes, setProps) {
    const { mode: modeStr, style = {} } = drawingConfig;
    const modeInstance = getModeInstance(modeStr);
    if (!modeInstance) {
        console.warn(`Unknown drawing mode: ${modeStr}`);
        return null;
    }

    const mergedStyle = { ...DEFAULT_STYLE, ...style };
    const isSelectionMode = SELECTION_MODES.has(modeStr);

    return new EditableGeoJsonLayer({
        id: '__drawing-layer',
        data: features,
        mode: modeInstance,
        selectedFeatureIndexes: selectedIndexes,

        // Committed feature styles — highlight selected features differently
        getFillColor: (feature, { index }) =>
            selectedIndexes.includes(index) ? mergedStyle.selectedFillColor : mergedStyle.fillColor,
        getLineColor: (feature, { index }) =>
            selectedIndexes.includes(index) ? mergedStyle.selectedLineColor : mergedStyle.lineColor,
        getLineWidth: () => mergedStyle.lineWidth,

        // Point size
        getRadius: () => mergedStyle.pointRadius,
        pointRadiusMinPixels: mergedStyle.pointRadius,
        pointRadiusUnits: 'pixels',

        // Tentative (in-progress) feature styles
        getTentativeFillColor: () => mergedStyle.tentativeFillColor,
        getTentativeLineColor: () => mergedStyle.tentativeLineColor,
        getTentativeLineWidth: () => mergedStyle.lineWidth,

        // Edit handle styles
        getEditHandlePointColor: () => mergedStyle.editHandlePointColor,
        editHandlePointRadiusScale: 4,
        editHandlePointRadiusMinPixels: 4,

        // Mode config — controls measurement tooltips
        modeConfig: mergedStyle.showMeasurements === false
            ? { formatTooltip: () => null }
            : {},

        // Picking
        pickable: true,
        autoHighlight: false,

        // Click handler for selection in modify/translate modes
        onClick: (info) => {
            if (isSelectionMode && info.index >= 0) {
                setSelectedIndexes([info.index]);
            }
        },

        // Edit callback
        onEdit: ({ updatedData, editType }) => {
            // Always update internal state for responsive UI
            setFeatures(updatedData);

            // Sync to Python on meaningful edits
            if (SYNC_EVENTS.has(editType) && setProps) {
                setProps({
                    drawingFeatures: updatedData,
                    drawingEvent: {
                        type: editType,
                        featureCount: updatedData.features.length,
                        timestamp: Date.now(),
                    },
                });
            }
        },
    });
}

/**
 * Delete features at the given indexes from a FeatureCollection
 * @param {object} featureCollection - GeoJSON FeatureCollection
 * @param {number[]} indexes - Indexes to delete
 * @returns {object} New FeatureCollection with features removed
 */
export function deleteFeatures(featureCollection, indexes) {
    const indexSet = new Set(indexes);
    return {
        type: 'FeatureCollection',
        features: featureCollection.features.filter((_, i) => !indexSet.has(i)),
    };
}
