/**
 * Layer Registry - Maps layer type names to deck.gl layer classes
 * Supports all deck.gl layer types from @deck.gl/layers, @deck.gl/geo-layers, and @deck.gl/aggregation-layers
 */

import { isScaleAccessor, parseScaleAccessor, createColorScaleAccessor } from './colorScales';
import { isEventEnabled } from './eventHandler';

// Core layers from @deck.gl/layers
import {
    ArcLayer,
    BitmapLayer,
    ColumnLayer,
    GeoJsonLayer,
    GridCellLayer,
    IconLayer,
    LineLayer,
    PathLayer,
    PointCloudLayer,
    PolygonLayer,
    ScatterplotLayer,
    SolidPolygonLayer,
    TextLayer,
} from '@deck.gl/layers';

// Geo layers from @deck.gl/geo-layers
import {
    GeohashLayer,
    GreatCircleLayer,
    H3ClusterLayer,
    H3HexagonLayer,
    MVTLayer,
    S2Layer,
    QuadkeyLayer,
    TerrainLayer,
    Tile3DLayer,
    TileLayer,
    TripsLayer,
} from '@deck.gl/geo-layers';

// Aggregation layers from @deck.gl/aggregation-layers
import {
    ContourLayer,
    GridLayer,
    HeatmapLayer,
    HexagonLayer,
    ScreenGridLayer,
} from '@deck.gl/aggregation-layers';

// Extensions from @deck.gl/extensions
import { DataFilterExtension } from '@deck.gl/extensions';

// Custom layers (local subclasses)
import MultiColorPathLayer from '../layers/MultiColorPathLayer';
import DirectedPathLayer from '../layers/DirectedPathLayer';

/**
 * Registry mapping extension @@type strings to extension classes.
 * Used to turn JSON-serializable `extensions` entries from Python into
 * real deck.gl extension instances (see instantiateExtensions).
 */
const EXTENSION_REGISTRY = {
    DataFilterExtension,
};

/**
 * Convert a layer config's `extensions` array (strings or {'@@type', ...opts} dicts)
 * into instantiated deck.gl extension objects. Unknown entries are dropped.
 * @param {Array} extensions - Raw extensions array from a layer config
 * @returns {Array} Array of extension instances
 */
function instantiateExtensions(extensions) {
    if (!Array.isArray(extensions)) {
        return [];
    }
    return extensions.map(ext => {
        if (typeof ext === 'string') {
            const ExtClass = EXTENSION_REGISTRY[ext];
            if (!ExtClass) {
                console.warn(`Unknown extension: ${ext}`);
                return null;
            }
            // DataFilterExtension defaults to a single scalar filter dimension.
            return ExtClass === DataFilterExtension ? new ExtClass({ filterSize: 1 }) : new ExtClass();
        }
        if (ext && typeof ext === 'object' && ext['@@type']) {
            const { '@@type': extType, ...opts } = ext;
            const ExtClass = EXTENSION_REGISTRY[extType];
            if (!ExtClass) {
                console.warn(`Unknown extension: ${extType}`);
                return null;
            }
            return new ExtClass(opts);
        }
        return null;
    }).filter(Boolean);
}

/**
 * Registry mapping @@type strings to layer classes
 */
const LAYER_REGISTRY = {
    // Core layers
    ArcLayer,
    BitmapLayer,
    ColumnLayer,
    GeoJsonLayer,
    GridCellLayer,
    IconLayer,
    LineLayer,
    PathLayer,
    PointCloudLayer,
    PolygonLayer,
    ScatterplotLayer,
    SolidPolygonLayer,
    TextLayer,

    // Custom layers
    MultiColorPathLayer,
    DirectedPathLayer,

    // Geo layers
    GeohashLayer,
    GreatCircleLayer,
    H3ClusterLayer,
    H3HexagonLayer,
    MVTLayer,
    S2Layer,
    QuadkeyLayer,
    TerrainLayer,
    Tile3DLayer,
    TileLayer,
    TripsLayer,

    // Aggregation layers
    ContourLayer,
    GridLayer,
    HeatmapLayer,
    HexagonLayer,
    ScreenGridLayer,
};

/**
 * Get a layer class by type name
 * @param {string} typeName - The layer type name (e.g., 'GeoJsonLayer', 'TileLayer')
 * @returns {Function|null} The layer class or null if not found
 */
export function getLayerClass(typeName) {
    return LAYER_REGISTRY[typeName] || null;
}

/**
 * Check if a layer type is registered
 * @param {string} typeName - The layer type name
 * @returns {boolean}
 */
export function isLayerRegistered(typeName) {
    return typeName in LAYER_REGISTRY;
}

/**
 * Get all registered layer type names
 * @returns {string[]}
 */
export function getRegisteredLayerTypes() {
    return Object.keys(LAYER_REGISTRY);
}

/**
 * Parse accessor string with @@= prefix to a function
 * Supports:
 * - Simple property path: "@@=properties.value" or "@@=coordinates[0]"
 * - Complex expressions: "@@=properties.count > 50 ? [255,0,0] : [0,0,255]"
 * - Color scale accessor: "@@scale(viridis, properties.count)" (handled separately)
 * @param {*} value - The value to parse (may be a string with @@= prefix or any other value)
 * @returns {*} A function if @@= syntax detected, @@scale string preserved, otherwise the original value
 */
export function parseAccessor(value) {
    if (typeof value !== 'string') {
        return value;
    }
    // Check for @@scale accessor - preserve as-is, will be resolved with data context
    if (isScaleAccessor(value)) {
        return value; // Return as-is, will be resolved in createLayer with data context
    }
    // Check for @@= accessor syntax
    if (value.startsWith('@@=')) {
        const expr = value.slice(3); // Remove '@@=' prefix
        // Check if this is a complex expression (contains operators) or simple path
        if (/[?:<>=!&|+\-*/%]/.test(expr)) {
            return createExpressionFunction(expr);
        }
        return createAccessorFunction(expr);
    }
    return value;
}

/**
 * Create an accessor function from a JavaScript expression
 * @param {string} expr - JavaScript expression like "properties.count > 50 ? [255,0,0] : [0,0,255]"
 * @returns {Function} Accessor function that evaluates the expression with the object
 */
function createExpressionFunction(expr) {
    // Create a function that evaluates the expression with the object's properties in scope
    // We use 'with' semantics by wrapping in a function that destructures common patterns
    try {
        // eslint-disable-next-line no-new-func
        const fn = new Function('d', `
            const properties = d.properties || {};
            const coordinates = d.coordinates || d.geometry?.coordinates || [];
            try {
                return ${expr};
            } catch(e) {
                return undefined;
            }
        `);
        return (object) => fn(object);
    } catch (e) {
        console.warn('Failed to parse accessor expression:', expr, e);
        return () => undefined;
    }
}

/**
 * Create an accessor function from a property path
 * @param {string} path - Property path like "properties.name" or "data[0].value"
 * @returns {Function} Accessor function that extracts the value from an object
 */
function createAccessorFunction(path) {
    // Split path into parts, handling both dot notation and bracket notation
    const parts = path.match(/[^.[\]]+/g) || [];
    return (object) => {
        let current = object;
        for (const part of parts) {
            if (current === null || current === undefined) {
                return undefined;
            }
            current = current[part];
        }
        return current;
    };
}

/**
 * Parse all accessors in a layer config object
 * @param {Object} config - Layer configuration object
 * @returns {Object} Config with accessor strings converted to functions
 */
export function parseLayerConfig(config) {
    const parsed = {};
    for (const [key, value] of Object.entries(config)) {
        if (key === '@@type' || key === 'id' || key === 'data' || key === 'extensions') {
            // Don't parse these special keys. `extensions` is copied verbatim here and
            // instantiated separately in createLayer (see instantiateExtensions).
            parsed[key] = value;
        } else if (Array.isArray(value)) {
            // Check if array contains accessor strings
            parsed[key] = value.map(item => parseAccessor(item));
        } else if (typeof value === 'object' && value !== null) {
            // Recursively parse nested objects
            parsed[key] = parseLayerConfig(value);
        } else {
            parsed[key] = parseAccessor(value);
        }
    }
    return parsed;
}

/**
 * Resolve @@scale accessors in parsed props using data context
 * @param {Object} props - Parsed layer props (may contain @@scale strings)
 * @param {Array|Object} data - Layer data (array or GeoJSON)
 * @returns {Object} Props with @@scale strings resolved to accessor functions
 */
function resolveScaleAccessors(props, data) {
    // Get the actual data array (handle GeoJSON FeatureCollection)
    let dataArray = data;
    if (data && data.type === 'FeatureCollection' && Array.isArray(data.features)) {
        dataArray = data.features;
    }
    if (!Array.isArray(dataArray)) {
        return props; // Can't compute domain without array data
    }

    const resolved = { ...props };
    for (const [key, value] of Object.entries(props)) {
        if (isScaleAccessor(value)) {
            const scaleConfig = parseScaleAccessor(value);
            if (scaleConfig) {
                resolved[key] = createColorScaleAccessor(scaleConfig, dataArray);
            }
        }
    }
    return resolved;
}

/**
 * Check if a URL appears to be a raster tile URL (PNG, JPG, etc.)
 * @param {string} url - The tile URL template
 * @returns {boolean}
 */
function isRasterTileUrl(url) {
    if (typeof url !== 'string') {
        return false;
    }
    // Common raster tile URL patterns
    const rasterPatterns = [
        /\.png$/i,
        /\.jpg$/i,
        /\.jpeg$/i,
        /\.webp$/i,
        /\{z\}.*\{x\}.*\{y\}.*\.png/i,
        /\{z\}.*\{x\}.*\{y\}.*\.jpg/i,
        /tile\.openstreetmap\.org/i,
        /tiles\.stadiamaps\.com/i,
        /basemaps\.cartocdn\.com.*\.png/i,
        /mt\d?\.google\.com/i,
        /api\.mapbox\.com.*tiles/i,
    ];
    return rasterPatterns.some(pattern => pattern.test(url));
}

/**
 * Create renderSubLayers function for raster TileLayer
 * This renders each tile as a BitmapLayer
 * @returns {Function}
 */
function createRasterTileRenderSubLayers() {
    return (props) => {
        const { tile, data } = props;
        const { boundingBox } = tile;
        // boundingBox is [[west, south], [east, north]]
        if (!data || !boundingBox) {
            return null;
        }
        return new BitmapLayer({
            id: `${props.id}-bitmap`,
            image: data,
            bounds: [
                boundingBox[0][0], // west
                boundingBox[0][1], // south
                boundingBox[1][0], // east
                boundingBox[1][1], // north
            ],
        });
    };
}

/**
 * Create a deck.gl layer instance from a JSON/dict configuration
 * @param {Object} config - Layer configuration with @@type property
 * @param {Object} options - Optional configuration for event callbacks
 * @param {Function} options.setProps - Dash setProps function for firing callbacks
 * @param {boolean|Array} options.enableEvents - Event configuration
 * @returns {Object|null} deck.gl layer instance or null if type not found
 */

// ===========================================
// Binary data transport (issue #39)
// ===========================================

const DTYPE_CONSTRUCTORS = {
    float32: Float32Array,
    float64: Float64Array,
    uint8: Uint8Array,
    uint16: Uint16Array,
    uint32: Uint32Array,
    int32: Int32Array,
};

// Pre-rendered tooltip strings for binary layers (no per-item object exists client-side)
const BINARY_TOOLTIPS = {};

/** Pre-rendered tooltip strings for a binary layer, or null. */
export function getBinaryTooltips(layerId) {
    return BINARY_TOOLTIPS[layerId] || null;
}

function base64ToArrayBuffer(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

/**
 * Rebuild a {'@@binary': ...} data block into deck.gl's native binary format:
 * {length, attributes: {name: {value: TypedArray, size}}, startIndices?}.
 * One base64 decode per layer; typed arrays are zero-copy views into the buffer.
 */
function rebuildBinaryData(block) {
    const buffer = base64ToArrayBuffer(block.buffer);
    const attributes = {};
    for (const [name, meta] of Object.entries(block.attributes || {})) {
        const Ctor = DTYPE_CONSTRUCTORS[meta.dtype];
        if (!Ctor) {
            console.warn(`Unsupported binary dtype '${meta.dtype}' for ${name}`);
            continue;
        }
        attributes[name] = {
            value: new Ctor(buffer, meta.offset, meta.byteLength / Ctor.BYTES_PER_ELEMENT),
            size: meta.size,
        };
    }
    const data = { length: block.length, attributes };
    if (block.startIndices) {
        const SICtor = DTYPE_CONSTRUCTORS[block.startIndices.dtype];
        data.startIndices = new SICtor(
            buffer,
            block.startIndices.offset,
            block.startIndices.byteLength / SICtor.BYTES_PER_ELEMENT
        );
    }
    return data;
}


export function createLayer(config, options = {}) {
    let { '@@type': typeName, ...layerProps } = config;

    // Binary data transport: rebuild typed arrays before any other processing
    if (layerProps.data && layerProps.data['@@binary']) {
        const block = layerProps.data['@@binary'];
        layerProps = { ...layerProps, data: rebuildBinaryData(block) };
        if (block.tooltips && layerProps.id) {
            BINARY_TOOLTIPS[layerProps.id] = block.tooltips;
        }
        // Composite PolygonLayer cannot take binary attributes; its solid core can
        if (typeName === 'PolygonLayer') {
            typeName = 'SolidPolygonLayer';
        }
    }
    if (!typeName) {
        console.warn('Layer config missing @@type:', config);
        return null;
    }
    const LayerClass = getLayerClass(typeName);
    if (!LayerClass) {
        console.warn(`Unknown layer type: ${typeName}. Available types:`, getRegisteredLayerTypes());
        return null;
    }
    // Parse accessors in the config
    let parsedProps = parseLayerConfig(layerProps);

    // Resolve @@scale accessors using data context
    if (parsedProps.data) {
        parsedProps = resolveScaleAccessors(parsedProps, parsedProps.data);
    }

    // Special handling for TileLayer with raster tiles
    if (typeName === 'TileLayer' && isRasterTileUrl(parsedProps.data)) {
        // Auto-configure renderSubLayers for raster tiles if not provided
        if (!parsedProps.renderSubLayers) {
            parsedProps.renderSubLayers = createRasterTileRenderSubLayers();
        }
    }

    // Inject data load event callbacks for layers with URL data
    const { setProps, enableEvents } = options;
    if (setProps && typeof parsedProps.data === 'string') {
        if (isEventEnabled('dataLoad', enableEvents)) {
            parsedProps.onDataLoad = (data) => {
                setProps({
                    dataLoadInfo: {
                        layerId: parsedProps.id || null,
                        featureCount: Array.isArray(data) ? data.length : (data?.features?.length ?? null),
                        timestamp: Date.now(),
                    }
                });
            };
        }
        if (isEventEnabled('dataLoadError', enableEvents)) {
            const existingOnError = parsedProps.onError;
            parsedProps.onError = (error) => {
                setProps({
                    dataLoadError: {
                        layerId: parsedProps.id || null,
                        error: error?.message || String(error),
                        timestamp: Date.now(),
                    }
                });
                if (existingOnError) existingOnError(error);
            };
        }
    }

    // Instantiate extensions (e.g. DataFilterExtension for GPU time filtering).
    // getFilterValue is parsed via the @@= accessor path above; filterRange /
    // filterSoftRange / filterEnabled are GPU uniforms that pass straight through.
    if (parsedProps.extensions) {
        parsedProps.extensions = instantiateExtensions(parsedProps.extensions);
    }

    try {
        return new LayerClass(parsedProps);
    } catch (error) {
        console.error(`Error creating ${typeName}:`, error);
        return null;
    }
}

/**
 * Create multiple deck.gl layers from an array of configurations
 * @param {Array} configs - Array of layer configurations
 * @param {Object} options - Optional configuration for event callbacks
 * @returns {Array} Array of deck.gl layer instances (excludes failed layers)
 */
export function createLayers(configs, options = {}) {
    if (!Array.isArray(configs)) {
        return [];
    }
    return configs.map(config => createLayer(config, options)).filter(layer => layer !== null);
}

// Re-export color scale utilities for external use
export { AVAILABLE_SCALES, colorRangeFromScale } from './colorScales';

export default LAYER_REGISTRY;
