# Binary Data Transport

For layers with hundreds of thousands to millions of items, the bottleneck is not
rendering — deck.gl handles 1M+ points at 60fps — it's getting the data to the GPU:
Python `json.dumps` over a million dicts, a huge JSON payload, client-side JSON
tokenization, and deck.gl walking a million JS objects to fill attribute buffers.

Binary transport (opt-in, per layer) packs numpy arrays into one aligned buffer that
the browser rebuilds into deck.gl's native `{length, attributes}` binary format with
a single base64 decode and zero-copy typed-array views.

**Measured, 1M points** (`getPosition` float32):

| | JSON rows | binary |
|---|---|---|
| Python serialize | 1.10 s | 0.02 s |
| Payload size | 48.9 MB | 10.7 MB |
| Client parse + attribute fill | ~170 ms | ~28 ms |

## Usage

```python
import numpy as np
from deckgl_dash import DeckGL
from deckgl_dash.layers import ScatterplotLayer

positions = np.asarray(points, dtype = np.float32)   # shape (n, 2)
colors = np.asarray(rgba, dtype = np.uint8)          # shape (n, 4)

# Option A: the per-layer flag — data is a dict of numpy arrays keyed by ACCESSOR name
layer = ScatterplotLayer(id = 'pts', use_binary = True, pickable = True, radius_min_pixels = 2,
                         data = {'getPosition': positions, 'getFillColor': colors})

# Option B: build the block explicitly (works with dict-style layers too)
from deckgl_dash.binary import binary_data
layer_config = {'@@type': 'ScatterplotLayer', 'id': 'pts', 'pickable': True,
                'data': binary_data(len(positions), {'getPosition': positions})}
```

dtype and component size are inferred from each array (`(n, 2)` float → `float32`,
size 2; pass an explicit `(array, dtype, size)` tuple to override). numpy is an
optional extra: `pip install deckgl-dash[binary]`.

### Variable-length geometry (paths / polygons)

Pass flattened vertices plus `startIndices` (uint32 offsets, one per feature):

```python
layer = PolygonLayer(id = 'polys', use_binary = True, data = {
    'getPolygon': flat_vertices_f32,          # (total_verts, 2)
    'startIndices': starts_u32,               # (n_polygons,)
})
```

Note: the composite `PolygonLayer` cannot take binary attributes — the component
automatically re-types it to `SolidPolygonLayer` (no outlines).

### Per-segment path colors

Per-segment coloring needs **no custom layer** in binary mode — the stock `PathLayer`
consumes a per-vertex color attribute directly (in JSON mode this requires
`multi_color=True`, which is incompatible with binary data and raises if combined):

```python
# One flattened vertex array for all paths, one RGBA color PER VERTEX
layer = PathLayer(id = 'tracks', use_binary = True, _path_type = 'open', width_min_pixels = 4,
                  data = {'getPath': verts_f32,       # (total_verts, 2)
                          'getColor': colors_u8,      # (total_verts, 4)
                          'startIndices': starts_u32})
```

Color placement: each segment takes the color of its **leading vertex** — for a path
of N points (N−1 segments), write segment *i*'s color at vertex *i*; the final
vertex's color is unused. `_path_type = 'open'` (or `'loop'`) is required so deck.gl
skips path normalization, which binary data cannot go through.

### Direction arrows on binary paths

`show_direction = True` works with binary data — the composite reads paths, colors,
and time-filter values straight from the packed attributes (arrows inherit each
segment's leading-vertex color, like the line):

```python
layer = PathLayer(id = 'tracks', use_binary = True, show_direction = True,
                  _path_type = 'open', arrow_spacing = 80, width_min_pixels = 3,
                  data = {'getPath': verts_f32, 'getColor': colors_u8,
                          'getFilterValue': fv_f32,        # optional: per-vertex; arrows use each path's first value
                          'startIndices': starts_u32})
```

Only `multi_color = True` remains incompatible with binary data (and unnecessary —
per-vertex colors are native); it raises with the pattern above.

## Picks and tooltips on binary layers

Binary layers have no per-item JS objects, so:

- **Pick events** still fire with `picked: true`, `layerId`, `index`, and
  `coordinate` — but `object`/`properties` are `null`. Back-fill in your callback by
  `(layer_id, index)` lookup into the source arrays/DataFrame Python-side.
- **Tooltips** must be pre-rendered Python-side — pass `tooltips = [...]` (one string
  per item) to `binary_data()` or as a `'tooltips'` key in the `use_binary` data
  dict; the browser looks them up by pick index.

## Design notes

- Buffer layout is ported from deckgl-marimo's `_binary.py`: attributes packed into a
  single buffer with per-attribute `{offset, byteLength, dtype, size}` metadata,
  aligned to each dtype's byte size; `startIndices` first when present.
- **Transport channel**: Dash has no sidecar binary channel (unlike anywidget's
  buffer protocol), so the buffer travels as base64 inside the normal `layers`/
  `layerData` JSON props. Base64 costs ~33% size overhead but skips JSON
  tokenization — the actual bottleneck — and decodes in a single pass. If payloads
  become the limit, alternatives (a Flask route serving raw ArrayBuffers, WebSocket
  push) can reuse the same metadata format.
- The JS rebuild (`layerRegistry.js`) creates typed arrays as zero-copy views into
  the decoded buffer via a dtype→constructor map.
- `float64` arrays are coerced to `float32` on packing (GPU precision; halves the
  payload) unless an explicit dtype tuple opts out.
