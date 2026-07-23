# AGENTS.md

## Project Overview

**auto-eatventure** is a Python automation bot for the Android mobile game "Eatventure". It uses ADB (Android Debug Bridge) to send input events and OpenCV template matching to detect game UI elements from screenshots. The bot runs an infinite game loop that upgrades food items, opens boxes/chests, and progresses through levels automatically.

- **Language**: Python 3.10+
- **Target**: physical Android device running Eatventure (`com.hwqgrhhjfd.idlefastfood`). An Android Studio emulator can run the bot too, but Eatventure requires a Google Play Games login, which Google Play now blocks on emulators — so progress cannot be saved/loaded there.
- **Interaction method**: ADB shell commands (tap, swipe, screencap)
- **Detection method**: OpenCV template matching with DBSCAN clustering

## Build & Run Commands

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `python adb_autoplay.py` | Run the bot (main entry point) |
| `start.bat` | Windows launch script (activates venv + runs bot) |
| `./start.sh` | Linux launch script (activates venv + runs bot) |
| `pylint adb_autoplay.py` | Lint the main script |

## Project Structure

```
adb_autoplay.py              # Entry point + main game loop (orchestration only)
device.py                    # ADB device interaction (click, swipe, screenshot)
template_matcher.py          # OpenCV template matching + DBSCAN clustering
game_actions.py              # High-level game actions (upgrade, boxes, chests, levels)
logger.py                    # Centralized logging config (console + file, daily rotation)
coords.py                    # Raw pixel coordinates (reference: 1220x2712)
scaled_coords.py             # Resolution-adaptive coordinate proxy
constants.py                 # Bundles scaled coords into {x,y} dicts
matching_screenshots/        # Template PNG images for OpenCV detection
  ads_crosses/               # Ad close button templates
captured_screenshots_on_the_fly/  # Runtime screenshots
logs/                        # Runtime log files (gitignored, daily rotation)
experiments/                 # Experimental scripts (investor, box detection)
.env-sample                  # Environment variable template
.pylintrc                    # Pylint configuration
start.bat / start.sh         # Launch scripts
requirements.txt             # Python dependencies
```

## Key Conventions

### Code Style
- Follow `.pylintrc`: 2-space indent, max 79 chars, LF line endings.
- KISS principle: keep implementations simple and readable (see `.github/agents/clean-code-implementer.agent.md`).
- Multi-module architecture: orchestration in `adb_autoplay.py`, details in dedicated modules.
- No unnecessary abstractions or design patterns.

### Coordinate System
- All pixel positions are defined in `coords.py` at reference resolution 1220x2712.
- Variables must use `_x` suffix for horizontal and `_y` suffix for vertical values.
- `ScaledCoords` auto-scales them; no manual scaling elsewhere.
- Non-pixel values (like `dbscan_eps`) must NOT have `_x`/`_y` suffix.

### Template Matching
- Templates stored in `matching_screenshots/` as PNG files.
- Templates are auto-resized at load time based on device resolution.
- Default matching threshold is 0.8; tune per-element as needed.
- Use HSV matching by default; grayscale or color-masked for specific cases.

### Environment
- Secrets and device config go in `.env` (gitignored).
- Use `os.getenv()` with sensible defaults for all env vars.
- Never commit `.env`; only `.env-sample` is tracked.

### Adding New Game Actions
1. Capture a template screenshot of the UI element.
2. Save it to `matching_screenshots/` as PNG.
3. Add path to `self.matching_screenshots_path` dict in `TemplateMatcher.__init__()`.
4. Add detection method (`is_having_*` or `get_*`) in `game_actions.py`.
5. Add coordinates to `coords.py` if tap targets are needed.
6. Add coordinate dicts to `constants.py`.
7. Integrate into the game loop in `start_playing_game()`.

## Topic Guides

- **[Architecture](docs/agents/architecture.md)** - Module responsibilities, data flow, state management, and design decisions.
- **[Template Matching](docs/agents/template-matching.md)** - OpenCV matching strategies, DBSCAN clustering, thresholds, and template catalog.
- **[Game Loop](docs/agents/game-loop.md)** - Main loop structure, periodic actions, level transitions, and recovery logic.
- **[Coordinates and Scaling](docs/agents/coordinates-and-scaling.md)** - Resolution-independent coordinate system and how to add new coordinates.
- **[ADB Interaction](docs/agents/adb-interaction.md)** - Device connection, input commands, screenshot capture, and platform differences.
- **[Logging](docs/agents/logging.md)** - Centralized logging setup, log levels, daily rotation, and configuration.
- **[Development Setup](docs/agents/development-setup.md)** - Prerequisites, quick start, dependencies, linting, and environment configuration.
