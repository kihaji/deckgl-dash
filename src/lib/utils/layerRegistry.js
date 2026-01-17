/**
 * Layer Registry - Maps layer type names to deck.gl layer classes
 * Supports all deck.gl layer types from @deck.gl/layers, @deck.gl/geo-layers, and @deck.gl/aggregation-layers
 */

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
 * Supports property path syntax like "@@=properties.value" or "@@=coordinates[0]"
 * @param {*} value - The value to parse (may be a string with @@= prefix or any other value)
 * @returns {*} A function if @@= syntax detected, otherwise the original value
 */
export function parseAccessor(value) {
    if (typeof value !== 'string') {
        return value;
    }
    // Check for @@= accessor syntax
    if (value.startsWith('@@=')) {
        const path = value.slice(3); // Remove '@@=' prefix
        return createAccessorFunction(path);
    }
    return value;
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
        if (key === '@@type' || key === 'id' || key === 'data') {
            // Don't parse these special keys
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
 * @returns {Object|null} deck.gl layer instance or null if type not found
 */
export function createLayer(config) {
    const { '@@type': typeName, ...layerProps } = config;
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
    const parsedProps = parseLayerConfig(layerProps);

    // Special handling for TileLayer with raster tiles
    if (typeName === 'TileLayer' && isRasterTileUrl(parsedProps.data)) {
        // Auto-configure renderSubLayers for raster tiles if not provided
        if (!parsedProps.renderSubLayers) {
            parsedProps.renderSubLayers = createRasterTileRenderSubLayers();
        }
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
 * @returns {Array} Array of deck.gl layer instances (excludes failed layers)
 */
export function createLayers(configs) {
    if (!Array.isArray(configs)) {
        return [];
    }
    return configs.map(config => createLayer(config)).filter(layer => layer !== null);
}

export default LAYER_REGISTRY;
