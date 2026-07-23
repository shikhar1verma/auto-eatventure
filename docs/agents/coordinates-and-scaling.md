# Coordinates and Resolution Scaling

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The coordinate system supports **any device resolution** from a single set of reference values calibrated at **1220x2712 pixels**. Three modules work together to provide resolution-independent coordinates.

## Module Chain

```
coords.py (raw values at 1220x2712)
    |
    v
scaled_coords.py (ScaledCoords proxy - scales by device ratio)
    |
    v
constants.py (Constants - bundles into {x, y} dicts)
    |
    v
game_actions.py (uses self.loc.xxx for all interactions)
```

## coords.py

Pure data module at project root. Contains:

- `REFERENCE_WIDTH = 1220` and `REFERENCE_HEIGHT = 2712`
- All tap coordinates (buttons, menus, UI elements)
- All swipe start/end coordinates
- Y-boundary thresholds for safe zones
- Click offsets for fine-tuned positioning
- DBSCAN clustering parameter (`dbscan_eps = 10`)

### Naming Convention

All coordinate variables follow: `<element_name>_<x|y>`

```python
settings_x = 1134
settings_y = 161
swipe_layout_down_start_x = 646
swipe_layout_down_start_y = 1889
```

**Rule**: Variables with `_x` suffix are scaled horizontally, `_y` suffix vertically. Variables without these suffixes (e.g., `dbscan_eps`) pass through unscaled.

## scaled_coords.py

`ScaledCoords` uses Python's `__getattr__` to intercept attribute access:

```python
sc = ScaledCoords(actual_w, actual_h)
sc.settings_x    # returns round(1134 * (actual_w / 1220))
sc.settings_y    # returns round(161 * (actual_h / 2712))
sc.dbscan_eps    # returns 10 (no suffix, no scaling)
```

### Resolution Detection

`detect_resolution(device)` calls `device.shell("wm size")` and parses output like `"Physical size: 1080x2400"`.

## constants.py

`Constants` bundles coordinate pairs into dicts:

```python
self.settings_coords = {'x': sc.settings_x, 'y': sc.settings_y}
self.swipe_layout_down_coords = {
    'start': {'x': ..., 'y': ...},
    'end': {'x': ..., 'y': ...}
}
```

Used as: `self.device.click(self.loc.settings_coords)`

## Adding New Coordinates

1. Add raw pixel values to `coords.py` with `_x` / `_y` suffix
2. If it's a tap target, add a `{x, y}` dict in `constants.py`
3. If it's a swipe, add a `{start: {x, y}, end: {x, y}}` dict
4. Use via `self.loc.<name>_coords` in `game_actions.py`

## Key Boundaries and Thresholds

| Variable | Value | Purpose |
|----------|-------|---------|
| `danger_max_y` | 2200 | Items below this excluded from food detection |
| `food_icon_tooltip_boundary_y` | 1240 | Food icons above this need offset click |
| `food_icon_top_boundary_y` | 1100 | Icons above this trigger swipe-up |
| `dbscan_eps` | 10 | DBSCAN pixel distance (not scaled) |
