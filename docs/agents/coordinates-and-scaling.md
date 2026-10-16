# Coordinates and Resolution Scaling

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The coordinate system supports **any device resolution** from a single set of reference values calibrated at **1220x2712 pixels**. The `coords/` package provides resolution-independent positions.

## Module Chain

```
coords/geometry.py (Point, Region, Swipe)
    |
    v
coords/reference.py (positions at 1220x2712)
    |
    v
coords/scaled.py (ScaledCoords - scales by device ratio)
    |
    v
actions/*.py (game.coords.<name> for all interactions)
```

## coords/geometry.py

Three `NamedTuple`s:

- `Point(x, y)` -- a pixel on the screen (tap target)
- `Region(left, top, right, bottom)` -- a rectangle (search area; right and bottom excluded). `Region.around(point, half_width, half_height)` builds one around a point; `center`, `crop(image)`, `moved(dx, dy)`.
- `Swipe(start, end)` -- a swipe gesture between two `Point`s

## coords/reference.py

Pure data module. Contains:

- `REFERENCE_WIDTH = 1220` and `REFERENCE_HEIGHT = 2712`
- All tap targets as `Point` (buttons, menus, UI elements)
- All search areas as `Region` (names ending in `_roi`)
- All swipes as `Swipe`
- Y boundaries of safe zones and tap offsets as plain numbers

### Naming Convention

Positions are lowercase names. Plain numbers end in `_x` or `_y`:

```python
settings = Point(1134, 161)
settings_roi = Region.around(settings, 30, 30)
swipe_down = Swipe(Point(646, 1889), Point(646, 1239))
station_icon_max_y = 2200
side_button_zone_width_x = 180
```

**Rule**: `Point`, `Region` and `Swipe` are scaled in both directions. Numbers with the `_x` suffix are scaled horizontally, `_y` suffix vertically. Other values pass through unscaled; non-pixel values (counts, ratios, thresholds) live in the module that uses them, not here.

## coords/scaled.py

`ScaledCoords` uses Python's `__getattr__` to intercept attribute access:

```python
sc = ScaledCoords(actual_w, actual_h)
sc.settings              # Point(round(1134 * actual_w / 1220),
                         #       round(161 * actual_h / 2712))
sc.station_icon_max_y    # round(2200 * actual_h / 2712)
sc.first_dish_candidates # tuple of scaled Points
```

It also has `x_scale`, `y_scale` and `screen_width`. An unknown name raises `AttributeError` naming `coords/reference.py`.

### Resolution Detection

`Device.screen_size()` (`android/device.py`) runs `wm size` and parses output like `"Physical size: 1080x2400"`. `bot/main.py` creates `ScaledCoords` from it; actions read it as `game.coords`.

## Adding New Coordinates

1. Add the position to `coords/reference.py`: `Point` for a tap target, `Region` for a search area, `Swipe` for a swipe, a number with `_x` / `_y` suffix for an offset or boundary
2. Use it as `game.coords.<name>` in an `actions/` module, e.g. `game.device.tap(game.coords.<name>)` or `game.screen.find('<template>', game.coords.<name>_roi)`

## Key Boundaries and Thresholds

| Variable | Value | Purpose |
|----------|-------|---------|
| `station_icon_max_y` | 2200 | Icons below this are ignored (club button, red badge of the Upgrades button) |
| `station_icon_tooltip_y` | 1240 | Icons above this need a special tap to avoid the tooltip |
| `station_icon_min_y` | 1100 | Icons above this trigger a swipe up |
| `side_button_zone_width_x` | 180 | Station taps keep this far from the screen edges |

The DBSCAN pixel distance (`CLUSTER_MAX_DISTANCE = 10`, not scaled) is in `vision/matching.py`.
