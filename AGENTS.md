# AGENTS.md

## Project Overview

**auto-eatventure** is a Python automation bot for the Android mobile game "Eatventure". It uses ADB (Android Debug Bridge) to send input events and OpenCV (template matching, color and shape checks) to detect game UI elements from screenshots. The bot runs an infinite game loop that upgrades food items, opens boxes/chests, and progresses through levels automatically.

- **Language**: Python 3.10+
- **Target**: physical Android device running Eatventure (`com.hwqgrhhjfd.idlefastfood`). An Android Studio emulator can run the bot too, but Eatventure requires a Google Play Games login, which Google Play now blocks on emulators — so progress cannot be saved/loaded there.
- **Interaction method**: ADB shell commands (tap, swipe, screencap)
- **Detection method**: OpenCV template matching (DBSCAN clustering for multiple matches), HSV color ratios, shape detection of the station upgrade icons

## Build & Run Commands

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `./start.sh` | Linux launch script (activates venv + runs bot) |
| `start.bat` | Windows launch script (activates venv + runs bot) |
| `PYTHONPATH=src python -m auto_eatventure` | Run the bot manually from the project root (Windows: `set PYTHONPATH=src`, then `python -m auto_eatventure`) |
| `PYTHONPATH=src python -m auto_eatventure.sandbox` | Interactive tool: screenshots, template crops, match tests |
| `pylint src/auto_eatventure` | Lint |

## Project Structure

```
src/auto_eatventure/         # The only package (src layout)
  __main__.py                # Entry point: python -m auto_eatventure
  main.py                    # run(): connect, wait for the game, play
  game_loop.py               # GameLoop: the endless loop (play_once)
  config.py                  # Settings from .env (feature switches, logs)
  timer.py                   # Timer: when an occasional action is due
  logger.py                  # setup_logging(), key_log (daily rotation)
  sandbox.py                 # Interactive testing tool
  actions/                   # Game actions, one module per feature
    game.py                  # Game: device + screen + coords + null_spot
    start_dialogs.py         # wait_until_ready, LateDialogWatch
    null_spot.py             # Spot tapped to close station popups
    stations.py              # Station upgrade icons: find, upgrade, scroll
    upgrades.py              # Upgrades dialog (red badge)
    boxes.py, chests.py      # Food boxes, chests of a new level
    levels.py                # Renovate / fly to the next city
    popups.py                # Red X popups, dimmed screen
    race_reward.py           # "Restaurant Race ended!" Claim
    stale.py                 # StaleWatch: recovery + search swipes
    popular_dish.py, food_delivery.py, helper_invite.py, adventures.py
                             # Optional features (see .env-sample)
  android/device.py          # Device: ADB taps, swipes, screenshots, app
  vision/                    # Detection on screenshots
    screen.py                # Screen: last screenshot + find/has/...
    templates.py             # TEMPLATE_NAMES catalog, loading, resizing
    matching.py              # OpenCV template matching + DBSCAN
    colors.py                # HSV color ranges, color_ratio()
    upgrade_icons.py         # Station upgrade icons by shape + color
    top_bar.py               # Black line at the bottom of the top bar
  coords/                    # Screen positions
    reference.py             # Positions at the reference 1220x2712
    geometry.py              # Point, Region, Swipe
    scaled.py                # ScaledCoords: reference.py scaled
matching_screenshots/        # Template PNG images for OpenCV detection
captured_screenshots_on_the_fly/  # Screenshots saved by the sandbox
logs/                        # Runtime log files (gitignored, daily rotation)
experiments/                 # Notes and scripts of feature investigations
.env-sample                  # Environment variable template
.pylintrc                    # Pylint configuration
start.bat / start.sh         # Launch scripts
requirements.txt             # Python dependencies
```

## Key Conventions

### Layout
- src layout with one package: all code is in `src/auto_eatventure/`; the root holds only data, docs and start scripts.
- Imports are absolute: `from auto_eatventure.actions import popups`, `from auto_eatventure import config`.
- Run from the project root with `PYTHONPATH=src` (or via `start.sh` / `start.bat`); data paths (`matching_screenshots/`, `logs/`, `captured_screenshots_on_the_fly/`, `.env`) are relative to it.
- Code paths below (`actions/stations.py`, `config.py`, ...) are relative to `src/auto_eatventure/`.

### Code Style
- Follow `.pylintrc`: 2-space indent, max 79 chars, LF line endings.
- KISS principle: keep implementations simple and readable (see `.github/agents/clean-code-implementer.agent.md`).
- Orchestration in `game_loop.py`, details in the `actions/`, `vision/`, `android/` and `coords/` modules.
- Game actions are plain functions taking a `game` (`actions/game.py`); a class only where state is kept between loops (`StaleWatch`, `LateDialogWatch`, `Timer`).
- Each module logs via `logging.getLogger(__name__)`; key milestones also via `key_log` from `logger.py`.
- No unnecessary abstractions or design patterns.

### Coordinate System
- All screen positions are defined in `coords/reference.py` at reference resolution 1220x2712.
- Tap targets are `Point`, search areas `Region`, swipes `Swipe` (`coords/geometry.py`).
- Plain numbers must use the `_x` suffix for horizontal and `_y` for vertical pixel values.
- `ScaledCoords` auto-scales them (read as `game.coords.<name>`); no manual scaling elsewhere.
- Non-pixel values (counts, ratios, thresholds) belong in the module that uses them, not in `coords/`.

### Template Matching
- Templates stored in `matching_screenshots/` as PNG files and listed in `TEMPLATE_NAMES` (`vision/templates.py`).
- Templates are auto-resized at load time based on device resolution.
- Default matching threshold is 0.8; tune per-element as needed.
- Use HSV matching by default (`Screen.find()` / `has()`); `find_exact()` (BGR, brightness-sensitive) and `find_all()` (BGR + DBSCAN) for specific cases.
- Search in a `Region` when the element has a known area.

### Environment
- Secrets and device config go in `.env` (gitignored).
- Env vars are read only in `config.py`, with sensible defaults.
- Never commit `.env`; only `.env-sample` is tracked.

### Adding New Game Actions
1. Capture a screenshot of the UI element (`PYTHONPATH=src python -m auto_eatventure.sandbox`), crop the template and save it to `matching_screenshots/` as PNG.
2. Add its file name (without `.png`) to `TEMPLATE_NAMES` in `vision/templates.py`.
3. Add positions to `coords/reference.py`: tap targets as `Point`, search areas as `Region` (e.g. `Region.around(point, ...)`), swipes as `Swipe`.
4. Add a module in `actions/` with plain functions taking `game` (detect with `game.screen.find/has(...)`, tap with `game.device.tap(game.coords.<name>)`).
5. Wire it into `GameLoop.play_once()` in `game_loop.py` (use a `Timer` for occasional actions).
6. If the feature is optional, add a switch in `config.py`, document it in `.env-sample` and log it in `_log_features()` (`main.py`).

## Topic Guides

- **[Architecture](docs/agents/architecture.md)** - Package and module responsibilities, data flow, state management, and design decisions.
- **[Template Matching](docs/agents/template-matching.md)** - OpenCV matching strategies, DBSCAN clustering, thresholds, and template catalog.
- **[Game Loop](docs/agents/game-loop.md)** - Main loop structure, periodic actions, level transitions, and recovery logic.
- **[Coordinates and Scaling](docs/agents/coordinates-and-scaling.md)** - Resolution-independent coordinate system and how to add new coordinates.
- **[ADB Interaction](docs/agents/adb-interaction.md)** - Device connection, input commands, screenshot capture, and platform differences.
- **[Logging](docs/agents/logging.md)** - Centralized logging setup, log levels, daily rotation, and configuration.
- **[Development Setup](docs/agents/development-setup.md)** - Prerequisites, quick start, dependencies, linting, and environment configuration.
