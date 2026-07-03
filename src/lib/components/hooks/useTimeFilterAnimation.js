/**
 * Time-filter rAF animation engine: advances the sliding-window head time while
 * playing and pushes the GPU filterRange to whichever renderer is live (MapLibre
 * overlay or deck-only instance) without rebuilding layers. Extracted verbatim
 * from DeckGL.react.js.
 */
import { useEffect, useCallback, useRef } from 'react';
import { applyRangeToLayers, resolveHeadTime } from '../../utils/timeFilter';

// Throttle interval for reporting the playback head time back to Dash (~8 Hz).
const REPORT_INTERVAL_MS = 120;

export function useTimeFilterAnimation({ timeFilter, allLayers, overlayRef, deckRef, setProps }) {
    // Always-fresh read of the timeFilter prop so the rAF loop sees play/pause/speed
    // changes without being torn down and restarted.
    const timeFilterRef = useRef(timeFilter);
    timeFilterRef.current = timeFilter;

    const rafRef = useRef(null);
    const headTimeRef = useRef(null);     // mutable playback head T (avoids a render per frame)
    const lastFrameTsRef = useRef(null);  // rAF timestamp of the previous frame
    const lastReportedRef = useRef(0);    // throttle clock for setProps({currentTime})
    // Base layers the engine clones from each frame; kept in sync with allLayers below.
    const currentDeckLayersRef = useRef(allLayers);
    currentDeckLayersRef.current = allLayers;

    // Lazily seed the head time the first time a timeFilter appears.
    if (timeFilter && headTimeRef.current === null) {
        headTimeRef.current = resolveHeadTime(timeFilter, null);
    }

    // Push the window's filterRange to the active renderer without rebuilding layers.
    const applyFilterRange = useCallback((T) => {
        const tf = timeFilterRef.current;
        if (!tf) return;
        const next = applyRangeToLayers(currentDeckLayersRef.current, T, tf);
        if (overlayRef.current) {
            overlayRef.current.setProps({ layers: next });
        } else if (deckRef.current && deckRef.current.deck) {
            deckRef.current.deck.setProps({ layers: next });
        }
    }, [overlayRef, deckRef]);

    // The animation frame: advance the head, apply the GPU uniform, throttle the report.
    const tick = useCallback((ts) => {
        const tf = timeFilterRef.current;
        if (!tf) { rafRef.current = null; return; }
        if (lastFrameTsRef.current == null) lastFrameTsRef.current = ts;
        const dt = (ts - lastFrameTsRef.current) / 1000; // seconds
        lastFrameTsRef.current = ts;

        if (tf.playing) {
            const domain = Array.isArray(tf.domain) ? tf.domain : [0, 0];
            const w = tf.window || 0;
            const speed = typeof tf.speed === 'number' ? tf.speed : (domain[1] - domain[0]) / 20;
            const loop = tf.loop !== false;
            const start = domain[0] + w;
            const end = domain[1];
            let T = (headTimeRef.current == null ? start : headTimeRef.current) + speed * dt;
            if (T > end) {
                const span = end - start;
                T = (loop && span > 0) ? start + ((T - start) % span) : (loop ? start : end);
            }
            headTimeRef.current = T;
            applyFilterRange(T);
            if (ts - lastReportedRef.current >= REPORT_INTERVAL_MS) {
                lastReportedRef.current = ts;
                if (setProps) setProps({ currentTime: T });
            }
        }
        rafRef.current = requestAnimationFrame(tick);
    }, [applyFilterRange, setProps]);

    // Run the rAF loop only while playing; stop on pause/unmount (resets dt so resume
    // does not jump).
    useEffect(() => {
        const playing = Boolean(timeFilter && timeFilter.playing);
        if (playing && rafRef.current == null) {
            lastFrameTsRef.current = null;
            rafRef.current = requestAnimationFrame(tick);
        } else if (!playing && rafRef.current != null) {
            cancelAnimationFrame(rafRef.current);
            rafRef.current = null;
        }
        return () => {
            if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
        };
    }, [timeFilter, tick]);

    // Paused scrubbing: when stopped, the incoming `current` is authoritative.
    useEffect(() => {
        if (!timeFilter || timeFilter.playing) return;
        if (typeof timeFilter.current === 'number') {
            headTimeRef.current = timeFilter.current;
            applyFilterRange(timeFilter.current);
        }
    }, [timeFilter?.current, timeFilter?.playing, timeFilter?.window, applyFilterRange]);

    // Re-apply the current window when base layers change mid-playback (deferred load,
    // visibility toggle, data update) so freshly built instances inherit the filter.
    useEffect(() => {
        if (timeFilterRef.current && headTimeRef.current != null) {
            applyFilterRange(headTimeRef.current);
        }
    }, [allLayers, applyFilterRange]);

    return { timeFilterRef, headTimeRef };
}
