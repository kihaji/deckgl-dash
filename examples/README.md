# Examples

Run any example with `poetry run python examples/<name>.py` and open the printed URL.
Each demo shows one feature; `_common.py` holds shared sample data and basemap helpers.

| Feature | Example |
|---|---|
| Minimal map (JSON layers, bare TileLayer basemap) | [`basic_usage.py`](basic_usage.py) |
| Python layer helpers tour | [`python_helpers_demo.py`](python_helpers_demo.py) |
| MapLibre basemap (vector styles) | [`maplibre_demo.py`](maplibre_demo.py) |
| MapLibre vector tile styling | [`maplibre_vector_demo.py`](maplibre_vector_demo.py) |
| MapLibre WMS sources | [`maplibre_wms_demo.py`](maplibre_wms_demo.py) |
| Runtime basemap switching | [`maplibre_basemap_switch_demo.py`](maplibre_basemap_switch_demo.py) |
| Drawing & editing (all modes incl. delete) | [`drawing_demo.py`](drawing_demo.py) |
| Per-segment path coloring | [`multicolor_path_demo.py`](multicolor_path_demo.py) |
| Direction-of-travel arrows | [`directed_path_demo.py`](directed_path_demo.py) |
| Time slider / GPU sliding-window animation | [`time_slider_demo.py`](time_slider_demo.py) |
| Deferred load & visibility toggles (all layer types) | [`all_layers_deferred_visibility_demo.py`](all_layers_deferred_visibility_demo.py) |
| Click → coordinate conversion (UTM/MGRS) | [`coordinate_click_demo.py`](coordinate_click_demo.py) |
| Feature list → map highlight linking | [`feature_list_highlight_demo.py`](feature_list_highlight_demo.py) |
| Fit camera to bounds | [`zoom_to_fit_demo.py`](zoom_to_fit_demo.py) |
| Bitmap overlay (satellite image) | [`performance_test_demo.py`](performance_test_demo.py) — also 1M-point stress test |
