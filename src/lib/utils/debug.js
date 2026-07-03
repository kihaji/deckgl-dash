/**
 * Debug/performance logging, gated behind a single flag.
 * Set DEBUG_PERF to true to enable console logging and timers.
 */
export const DEBUG_PERF = false;
export const debugLog = DEBUG_PERF ? (...args) => console.log('[DeckGL]', ...args) : () => {};
export const debugTime = DEBUG_PERF ? (label) => console.time(label) : () => {};
export const debugTimeEnd = DEBUG_PERF ? (label) => console.timeEnd(label) : () => {};
