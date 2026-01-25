/**
 * Color Scales - Chroma.js integration for deck.gl color accessors
 *
 * Supports the @@scale syntax for data-driven color mapping:
 * - @@scale(viridis, properties.count)                    // Auto-domain
 * - @@scale(viridis, properties.count, 0, 100)           // Explicit domain
 * - @@scale(OrRd, properties.value, 0, 1000, 200)        // With alpha
 * - @@scale(Spectral:reverse, properties.temp, -10, 40)  // Reversed
 * - @@scale(viridis:log, properties.population)          // Logarithmic
 * - @@scale(plasma:log:reverse, properties.value, 1, 1000) // Combined modifiers
 */

import chroma from 'chroma-js';

/**
 * Available color scales from chroma.js
 * Sequential, diverging, and perceptually uniform scales
 */
export const AVAILABLE_SCALES = [
    // Sequential
    'OrRd', 'PuBu', 'BuPu', 'Oranges', 'BuGn', 'YlOrBr', 'YlGn', 'Reds',
    'RdPu', 'Greens', 'YlGnBu', 'Purples', 'GnBu', 'Greys', 'YlOrRd',
    'PuRd', 'Blues', 'PuBuGn',
    // Diverging
    'Spectral', 'RdYlGn', 'RdBu', 'PiYG', 'PRGn', 'RdYlBu', 'BrBG', 'RdGy', 'PuOr',
    // Perceptually uniform
    'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'turbo',
];

/**
 * Parse @@scale(...) accessor string
 * @param {string} value - String starting with '@@scale('
 * @returns {Object|null} Parsed scale config or null if invalid
 *
 * Returns: { scaleName, modifiers: { reverse, log, sqrt }, propertyPath, min, max, alpha }
 */
export function parseScaleAccessor(value) {
    if (typeof value !== 'string' || !value.startsWith('@@scale(')) {
        return null;
    }

    // Extract content between @@scale( and )
    const match = value.match(/^@@scale\((.+)\)$/);
    if (!match) {
        console.warn('Invalid @@scale syntax:', value);
        return null;
    }

    const content = match[1];
    // Split by comma, but be careful with nested expressions
    const parts = splitScaleParams(content);

    if (parts.length < 2) {
        console.warn('@@scale requires at least scale name and property path:', value);
        return null;
    }

    // Parse scale name and modifiers (e.g., "viridis:log:reverse")
    const [scalePart, propertyPath, minStr, maxStr, alphaStr] = parts.map(p => p.trim());
    const { scaleName, modifiers } = parseScaleName(scalePart);

    // Validate scale name
    if (!AVAILABLE_SCALES.includes(scaleName)) {
        console.warn(`Unknown scale '${scaleName}'. Available:`, AVAILABLE_SCALES);
        return null;
    }

    const result = {
        scaleName,
        modifiers,
        propertyPath,
        min: minStr !== undefined ? parseFloat(minStr) : null,
        max: maxStr !== undefined ? parseFloat(maxStr) : null,
        alpha: alphaStr !== undefined ? parseInt(alphaStr, 10) : 255,
    };

    // Validate domain if both provided
    if (result.min !== null && result.max !== null && result.min >= result.max) {
        console.warn('@@scale min must be less than max:', value);
        return null;
    }

    return result;
}

/**
 * Split scale parameters, handling potential nested expressions
 * @param {string} content - Content inside @@scale(...)
 * @returns {string[]} Array of parameter strings
 */
function splitScaleParams(content) {
    const parts = [];
    let current = '';
    let depth = 0;

    for (const char of content) {
        if (char === '(' || char === '[') {
            depth++;
            current += char;
        } else if (char === ')' || char === ']') {
            depth--;
            current += char;
        } else if (char === ',' && depth === 0) {
            parts.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    if (current) {
        parts.push(current);
    }

    return parts;
}

/**
 * Parse scale name with modifiers
 * @param {string} scalePart - e.g., "viridis:log:reverse"
 * @returns {{ scaleName: string, modifiers: { reverse: boolean, log: boolean, sqrt: boolean } }}
 */
function parseScaleName(scalePart) {
    const parts = scalePart.split(':');
    const scaleName = parts[0];
    const modifiers = {
        reverse: false,
        log: false,
        sqrt: false,
    };

    for (let i = 1; i < parts.length; i++) {
        const mod = parts[i].toLowerCase();
        if (mod === 'reverse') modifiers.reverse = true;
        else if (mod === 'log') modifiers.log = true;
        else if (mod === 'sqrt') modifiers.sqrt = true;
        else console.warn(`Unknown scale modifier: ${mod}`);
    }

    return { scaleName, modifiers };
}

/**
 * Create an accessor function from a property path
 * @param {string} path - Property path like "properties.count"
 * @returns {Function} Function that extracts value from an object
 */
function createPropertyAccessor(path) {
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
 * Compute min/max domain from data array
 * @param {Array} data - Array of feature objects
 * @param {Function} accessor - Function to extract value from each feature
 * @returns {{ min: number, max: number }}
 */
export function computeDomain(data, accessor) {
    let min = Infinity;
    let max = -Infinity;

    for (const item of data) {
        const value = accessor(item);
        if (typeof value === 'number' && !isNaN(value)) {
            if (value < min) min = value;
            if (value > max) max = value;
        }
    }

    // Handle edge cases
    if (min === Infinity || max === -Infinity) {
        return { min: 0, max: 1 };
    }
    if (min === max) {
        return { min: min - 0.5, max: max + 0.5 };
    }

    return { min, max };
}

/**
 * Create a color scale accessor function
 * @param {Object} config - Parsed scale configuration
 * @param {Array} data - Data array for auto-domain computation
 * @returns {Function} Accessor function that returns [r, g, b, a] for each feature
 */
export function createColorScaleAccessor(config, data) {
    const { scaleName, modifiers, propertyPath, min, max, alpha } = config;
    const propertyAccessor = createPropertyAccessor(propertyPath);

    // Compute domain if not provided
    let domainMin = min;
    let domainMax = max;
    if (domainMin === null || domainMax === null) {
        const computed = computeDomain(data, propertyAccessor);
        if (domainMin === null) domainMin = computed.min;
        if (domainMax === null) domainMax = computed.max;
    }

    // For log scale, ensure positive values
    if (modifiers.log && domainMin <= 0) {
        console.warn(`Log scale requires positive values. Clamping min from ${domainMin} to 0.001`);
        domainMin = 0.001;
    }

    // Create chroma scale
    let scale = chroma.scale(scaleName);
    if (modifiers.reverse) {
        scale = scale.domain([1, 0]); // Reverse by inverting domain
    }

    // Return accessor function
    return (object) => {
        const value = propertyAccessor(object);
        if (typeof value !== 'number' || isNaN(value)) {
            return [128, 128, 128, alpha]; // Default gray for invalid values
        }

        // Compute normalized position (0-1)
        let t;
        if (modifiers.log) {
            // Logarithmic: t = log(value/min) / log(max/min)
            const clampedValue = Math.max(value, domainMin);
            t = Math.log(clampedValue / domainMin) / Math.log(domainMax / domainMin);
        } else if (modifiers.sqrt) {
            // Square root: t = sqrt((value-min) / (max-min))
            const normalized = (value - domainMin) / (domainMax - domainMin);
            t = Math.sqrt(Math.max(0, Math.min(1, normalized)));
        } else {
            // Linear: t = (value - min) / (max - min)
            t = (value - domainMin) / (domainMax - domainMin);
        }

        // Clamp to [0, 1]
        t = Math.max(0, Math.min(1, t));

        // Get color from scale
        const color = scale(t).rgb();
        return [Math.round(color[0]), Math.round(color[1]), Math.round(color[2]), alpha];
    };
}

/**
 * Check if a value is a @@scale accessor string
 * @param {*} value - Value to check
 * @returns {boolean}
 */
export function isScaleAccessor(value) {
    return typeof value === 'string' && value.startsWith('@@scale(');
}

/**
 * Generate a discrete color range array from a chroma scale
 * Useful for aggregation layers that need colorRange prop
 * @param {string} scaleName - Chroma scale name (e.g., 'viridis')
 * @param {number} steps - Number of colors to generate
 * @param {Object} options - Optional: { reverse: boolean }
 * @returns {number[][]} Array of [r, g, b] colors
 */
export function colorRangeFromScale(scaleName, steps = 6, options = {}) {
    const { reverse = false } = options;

    if (!AVAILABLE_SCALES.includes(scaleName)) {
        console.warn(`Unknown scale '${scaleName}'. Using 'viridis'.`);
        scaleName = 'viridis';
    }

    const scale = chroma.scale(scaleName).colors(steps);
    let colors = scale.map(c => {
        const rgb = chroma(c).rgb();
        return [Math.round(rgb[0]), Math.round(rgb[1]), Math.round(rgb[2])];
    });

    if (reverse) {
        colors = colors.reverse();
    }

    return colors;
}

export default {
    AVAILABLE_SCALES,
    parseScaleAccessor,
    createColorScaleAccessor,
    computeDomain,
    isScaleAccessor,
    colorRangeFromScale,
};
