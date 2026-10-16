# Architecture

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The project is a **multi-package Python bot** that automates the Android mobile game "Eatventure" via ADB and OpenCV. Each package has one concern: start-up and loop (`bot/`), game actions (`actions/`), the phone (`android/`), detection (`vision/`) and screen positions (`coords/`). Modules are small and focused.

## Core Architecture Diagram

```
adb_autoplay.py --- entry point, calls bot.main.run()
    |
    +-- bot/main.py --- logging, connect, wait for the game, start the loop
    |       |
    |       +-- bot/logger.py --- setup_logging(), key_log
    |       +-- bot/config.py --- settings from .env
    |
    +-- bot/game_loop.py (GameLoop) --- decides what to do next
    |       |
    |       +-- bot/timer.py (Timer) --- occasional actions
    |       +-- actions/*.py --- one module per game feature
    |
    +-- actions/game.py (Game) --- what every action works with
            |
            +-- android/device.py (Device) --- ADB taps, swipes, screenshots
            |
            +-- vision/screen.py (Screen) --- last screenshot, searches
            |       |
            |       +-- vision/templates.py --- TEMPLATE_NAMES, loading
            |       |       |
            |       |       +-- matching_screenshots/ --- PNG templates
            |       +-- vision/matching.py --- cv2.matchTemplate, DBSCAN
            |       +-- vision/colors.py --- HSV ranges, color_ratio()
            |
            +-- coords/scaled.py (ScaledCoords) --- scaled positions
            |       |
            |       +-- coords/reference.py --- positions at 1220x2712
            |       +-- coords/geometry.py --- Point, Region, Swipe
            |
            +-- null_spot --- Point tapped to close station popups
```

`vision/upgrade_icons.py` (station icons) and `vision/top_bar.py`
(top bar line) work on a screenshot array and are called from
`actions/stations.py` and `actions/null_spot.py`.

## Module Responsibilities

| Module | Main names | Responsibility |
|--------|------------|----------------|
| `adb_autoplay.py` | | Entry point, calls `bot.main.run()`. |
| `bot/main.py` | `run()` | Sets up logging, connects to the phone, loads the scaled templates, starts the game, waits until it is ready, places the null spot, logs the features, runs `GameLoop`. |
| `bot/game_loop.py` | `GameLoop` | The endless loop. `play_once()`: one screenshot, then the first action that applies. Keeps the loop state. |
| `bot/config.py` | constants | Settings from the environment / `.env` (device serial, feature switches, template debugging, log levels). |
| `bot/timer.py` | `Timer` | When an occasional action (Popular Dish, Adventures, ...) is due again. |
| `bot/logger.py` | `setup_logging()`, `key_log` | Console + daily-rotating file handlers in `logs/`, key events log, crash and stop logging. |
| `actions/game.py` | `Game` | Bundles `device`, `screen`, `coords` and `null_spot`; passed to every action function. |
| `actions/start_dialogs.py` | `wait_until_ready()`, `close_dimming_dialogs()`, `LateDialogWatch` | Dialogs at the start of the bot. |
| `actions/null_spot.py` | `place_below_top_bar()` | Places the null spot below the top bar at start. |
| `actions/stations.py` | `find_icons()`, `upgrade()`, `reposition_after_new_level()`, `scroll_if_icons_too_high()` | Station upgrade icons and restaurant scrolling. |
| `actions/upgrades.py` | `buy_if_available()` | Upgrades dialog. |
| `actions/boxes.py` | `open_all()` | Food boxes. |
| `actions/chests.py` | `open_all()` | Chests of a new level. |
| `actions/levels.py` | `go_to_next_level()`, `tap_welcome_okay()`, `tap_open_button()` | Renovate / fly to the next city and the dialogs after it. |
| `actions/popups.py` | `close_popup()`, `is_screen_dimmed()` | Red X popups, dimmed screen. |
| `actions/race_reward.py` | `claim()` | "Restaurant Race ended!" reward. |
| `actions/stale.py` | `StaleWatch` | Recovery and search swipes when nothing can be upgraded. |
| `actions/popular_dish.py`, `food_delivery.py`, `helper_invite.py`, `adventures.py` | | Optional features (switches in `bot/config.py`). |
| `android/device.py` | `Device` | ADB: `tap()`, `long_press()`, `swipe()`, `screenshot()` (BGR), `screen_size()`, `start_app()`, `close_app()`. |
| `vision/screen.py` | `Screen` | Last screenshot in BGR / gray / HSV; `capture()`, `find()`, `has()`, `find_exact()`, `find_all()`, `color_ratio()`. |
| `vision/templates.py` | `TEMPLATE_NAMES`, `load_templates()` | Template catalog, loading and resizing to the phone. |
| `vision/matching.py` | `best_match()`, `closest_match()`, `all_matches()` | OpenCV template matching, DBSCAN clustering. |
| `vision/colors.py` | `RED`, `color_ratio()` | HSV color ranges and their share of an image. |
| `vision/upgrade_icons.py` | `find_upgrade_icons()` | Station upgrade icons by shape and color. |
| `vision/top_bar.py` | `find_top_bar_line()` | Black line at the bottom of the top bar. |
| `coords/reference.py` | positions | All screen positions at 1220x2712. Pure data, no logic. |
| `coords/geometry.py` | `Point`, `Region`, `Swipe` | Shapes positions are made of. |
| `coords/scaled.py` | `ScaledCoords` | Scales `reference.py` to the phone's resolution. |

## Data Flow (One Iteration)

1. `GameLoop.play_once()` calls `game.screen.capture()`
2. `Screen` gets a BGR screenshot from `Device.screenshot()` (ADB) and keeps it as BGR, grayscale and HSV numpy arrays
3. Action functions search the current screenshot via `game.screen` (`find()`, `has()`, `color_ratio()`, ...) or pass `game.screen.hsv` to `vision/upgrade_icons.py`
4. `vision/matching.py` runs `cv2.matchTemplate()`; DBSCAN merges multiple matches of one object (`find_all()`)
5. Actions tap / swipe via `game.device` at positions from `game.coords`
6. Loop repeats

## State Management

State is purely **in-memory** in `GameLoop` and its helpers:

- `loops` -- iteration counter driving periodic actions
- `StaleWatch.idle_loops` -- consecutive loops with no station icon found (reset after stale recovery and on a new level)
- `needs_reposition` -- the first station icons of a level reposition the restaurant
- `popular_dish_waits_for_upgrade` -- after a level change Popular Dish waits for the first station upgrade
- `Timer`s of the optional features, `LateDialogWatch` for the first minute
- `game.null_spot` -- placed once at start

There is **no persistent state**, no database, no save files. The bot is purely reactive.

## Key Design Decisions

- **Separation of concerns**: orchestration in `bot/game_loop.py`, device I/O in `android/`, detection in `vision/`, positions in `coords/`, game logic in `actions/`.
- **Plain functions**: game actions are functions taking a `Game`; classes only where state is kept (`GameLoop`, `StaleWatch`, `LateDialogWatch`, `Timer`, `Screen`, `Device`).
- **KISS principle**: Each module has a single clear purpose. No inheritance hierarchies or complex patterns.
- **Resolution scaling**: One set of reference coordinates scales to any device resolution via `ScaledCoords`.
- **Template matching over OCR**: More reliable for Unity game UI where text rendering varies.
- **In-memory screenshots**: Avoids disk I/O on every iteration.
- **Clean game loop**: `play_once()` reads like a checklist of actions; implementation details live in `actions/`.
