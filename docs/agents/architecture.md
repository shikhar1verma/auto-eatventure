# Architecture

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The project is a **multi-module Python bot** that automates the Android mobile game "Eatventure" via ADB and OpenCV template matching. The architecture separates concerns into distinct modules while keeping each one simple and focused.

## Core Architecture Diagram

```
adb_autoplay.py (AutoEatventure - orchestrator)
    |
    +-- logger.py --- centralized logging (console + file)
    |
    +-- device.py (Device) --- ADB interaction layer
    |
    +-- template_matcher.py (TemplateMatcher) --- OpenCV detection engine
    |       |
    |       +-- matching_screenshots/ --- PNG template images
    |
    +-- game_actions.py (GameActions) --- game logic and actions
    |       |
    |       +-- uses Device for input
    |       +-- uses TemplateMatcher for detection
    |       +-- uses Constants for coordinates
    |
    +-- constants.py (Constants) --- coordinate dicts for click/swipe targets
    |       |
    |       +-- scaled_coords.py (ScaledCoords) --- resolution-adaptive proxy
    |               |
    |               +-- coords.py --- raw pixel values (reference: 1220x2712)
```

## Module Responsibilities

| Module | Class | Responsibility |
|--------|-------|---------------|
| `adb_autoplay.py` | `AutoEatventure` | Entry point. Initializes logging and all modules, runs the ~40-line game loop that calls high-level actions. |
| `logger.py` | (module-level) | Centralized logging configuration. Console handler (INFO default) + daily-rotating file handler (DEBUG default) writing to `logs/`. |
| `device.py` | `Device` | ADB device interaction: click, swipe, text input, screenshot capture, app lifecycle. |
| `template_matcher.py` | `TemplateMatcher` | Template loading/resizing, `find_template()`, `find_all_templates()` with DBSCAN, color masking, pixel color checks. |
| `game_actions.py` | `GameActions` | All game logic: detection helpers (`is_having_*`), game actions (upgrade, boxes, chests, levels), stale state recovery, layout adjustments. |
| `coords.py` | (module-level) | All reference-resolution pixel coordinates calibrated for 1220x2712. Pure data, no logic. |
| `scaled_coords.py` | `ScaledCoords` | Proxy that scales `coords.py` values to actual device resolution. `_x` suffix scales horizontally, `_y` suffix scales vertically. |
| `constants.py` | `Constants` | Bundles scaled coordinates into `{x, y}` dicts for cleaner call sites. |

## Data Flow (One Iteration)

1. `AutoEatventure.start_playing_game()` calls `device.capture_screenshot()`
2. `Device` captures screenshot via ADB, stores as BGR/grayscale/HSV numpy arrays
3. `GameActions` methods access the current frame via `device.current_cv2_sc_*`
4. `TemplateMatcher` runs `cv2.matchTemplate()` against relevant templates
5. DBSCAN deduplicates multi-match results into centroids
6. `GameActions` executes game actions (tap/swipe) via `Device`
7. Loop repeats

## State Management

State is purely **in-memory variables** in the game loop:

- `count` -- iteration counter driving periodic actions
- `nothing_to_update_count` -- consecutive frames with no food icons found
- `new_level_started` / `new_level_first_food_icon_swipe` -- post-level-transition flags
- `swipe_count` -- cycles through swipe pattern array

There is **no persistent state**, no database, no save files. The bot is purely reactive.

## Key Design Decisions

- **Separation of concerns**: orchestration in `adb_autoplay.py`, device I/O in `device.py`, detection in `template_matcher.py`, game logic in `game_actions.py`.
- **Flat file structure**: No `src/` directory. All core modules at project root.
- **KISS principle**: Each module has a single clear purpose. No inheritance hierarchies or complex patterns.
- **Resolution scaling**: One set of reference coordinates scales to any device resolution via `ScaledCoords`.
- **Template matching over OCR**: More reliable for Unity game UI where text rendering varies.
- **In-memory screenshots**: Avoids disk I/O on every iteration.
- **Clean game loop**: Main loop reads like a checklist of actions; implementation details hidden in methods.
