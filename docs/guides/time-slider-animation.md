# Time Slider & Animation

Filter visible data to a **sliding time window** and animate it across the full time range —
useful for pattern-of-life playback, time-series exploration, and "wave of activity" views.

## Why client-side?

For a dataset that fits in the browser, filtering on the server (resending data on every
slider tick) means a round trip per frame and can't hold 60fps. deckgl-dash instead:

- Ships the data to the browser **once**.
- Filters on the **GPU** via deck.gl's `DataFilterExtension` — `filterRange` is a uniform,
  so the sliding window costs almost nothing per frame.
- Drives playback with an internal `requestAnimationFrame` loop, so animation is **60fps**
  with **no per-frame server round trips**.
- Reports the playback head back to Dash as the throttled `current_time` output (~8 Hz), so
  a slider handle, readouts, and other callbacks can follow along.

## Three pieces

### 1. A `get_filter_value` accessor on each filterable layer

Give every layer you want filtered a per-datum numeric time value. Supplying
`get_filter_value` auto-attaches the `DataFilterExtension`:

```python
from deckgl_dash.layers import ScatterplotLayer

ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates',
                 get_filter_value='@@=t')  # extensions=['DataFilterExtension'] auto-added
```

Layers without `get_filter_value` (e.g. a basemap `TileLayer`) are never filtered.

!!! warning "Keep time values float32-safe"
    `DataFilterExtension` uploads filter values as **32-bit floats**. Raw epoch seconds
    (~1.7e9) exceed float32 integer precision (~16.7M) and the window will jump. Store time
    on a smaller scale — **seconds/days since the domain start** — or attach the extension
    with `fp64=True`: `extensions=[{'@@type': 'DataFilterExtension', 'fp64': True}]`.

### 2. A `time_filter` config

Build it with `build_time_filter`, using `compute_time_domain` to find the extent:

```python
from deckgl_dash import DeckGL, compute_time_domain, build_time_filter
from deckgl_dash.layers import TileLayer, ScatterplotLayer

DOMAIN = compute_time_domain(POINTS, 't')        # [t_min, t_max]
WINDOW = (DOMAIN[1] - DOMAIN[0]) * 0.1           # 10%-wide trailing window

DeckGL(
    id='map',
    layers=[
        TileLayer(id='basemap', data='https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
        ScatterplotLayer(id='points', data=POINTS, get_position='@@=coordinates',
                         get_filter_value='@@=t'),
    ],
    time_filter=build_time_filter(DOMAIN, WINDOW),   # playing=False by default
)
```

See the [`time_filter` field reference](../api/deckgl-component.md#time-filtering-and-animation)
for all keys (`domain`, `window`, `current`, `playing`, `speed`, `loop`, `soft_edge`,
`layer_ids`, `nonce`).

### 3. Controls wired to one callback

The cleanest pattern lets a single callback own the `time_filter` prop, the slider handle,
and a readout. The key subtlety is the **feedback loop**: during playback the engine pushes
`current_time`, which you echo to the slider's `value`; that echo re-fires the callback with
the slider as the trigger. Guard against it by **ignoring slider input while `playing`** — so
only genuine scrubbing (while paused) writes back to `time_filter`.

```python
from dash import Dash, dcc, html, callback, Output, Input, State, ctx, no_update

app.layout = html.Div([
    html.Button('▶ Play', id='btn-play', n_clicks=0),
    html.Button('⏸ Pause', id='btn-pause', n_clicks=0),
    dcc.Slider(id='time-slider', min=DOMAIN[0], max=DOMAIN[1],
               value=DOMAIN[0] + WINDOW, updatemode='drag'),
    html.Span(id='readout'),
    DeckGL(id='map', layers=[...], time_filter=build_time_filter(DOMAIN, WINDOW)),
])

@callback(
    Output('map', 'timeFilter'), Output('time-slider', 'value'), Output('readout', 'children'),
    Input('btn-play', 'n_clicks'), Input('btn-pause', 'n_clicks'),
    Input('time-slider', 'value'), Input('map', 'currentTime'),
    State('map', 'timeFilter'), prevent_initial_call=True,
)
def control(_play, _pause, slider_value, current_time, tf):
    tf = dict(tf)
    trig = ctx.triggered_id
    if trig == 'map':                       # playback tick: move handle + readout only
        return no_update, current_time, f't = {current_time:.1f}'
    if trig == 'btn-play':
        tf['playing'] = True;  return tf, no_update, no_update
    if trig == 'btn-pause':
        tf['playing'] = False; return tf, no_update, no_update
    if trig == 'time-slider':
        if tf.get('playing'):               # programmatic echo during playback — ignore
            return no_update, no_update, no_update
        tf['current'] = slider_value
        tf['nonce'] = (tf.get('nonce') or 0) + 1   # re-sync even if value is unchanged
        return tf, no_update, f't = {slider_value:.1f}'
    return no_update, no_update, no_update
```

## How playback works

- While `playing`, the head `current` advances by `speed` time-units per real second; the
  visible window is `[current - window, current]`.
- At the end it wraps to `domain[0] + window` (when `loop=True`) — an instantaneous jump,
  since a sliding window can't scroll backward seamlessly.
- While paused, the incoming `current` is authoritative, so the slider scrubs the window.
- `current_time` is reported ~8 Hz (the GPU still renders every frame); tune playback feel
  with `speed`, not the report rate.

## Tips & gotchas

- **Pick `window` relative to the domain** (e.g. 10–15% of the span) so a useful slice is
  visible at any moment.
- **`soft_edge`** maps to `filterSoftRange` for fade-in/out at the window edges instead of a
  hard pop.
- **Directed paths** (`show_direction=True`) filter together with their arrows — the line
  and arrows appear and disappear as one.
- **Aggregation layers** (Heatmap/Hexagon/Grid) accept `get_filter_value` via `**kwargs`,
  but re-aggregate as the window moves, which is heavier than a uniform swap — prefer
  primitive layers for smooth playback at scale.
- **Multiple layers** filter from the same `time_filter` automatically; restrict to specific
  layers with `layer_ids`.

## Examples

- `examples/time_slider_demo.py` — scatter points, Play/Pause/speed, scrubbable slider.
- `examples/directed_path_demo.py` — direction-of-travel arrows; combine with a time filter and
  the lines and arrows fade together.
