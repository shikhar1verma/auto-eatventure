# Development Setup

> <- Back to [AGENTS.md](../../AGENTS.md)

## Prerequisites

1. **Python 3.10+**
2. **A physical Android device** (recommended) or Android Studio emulator
3. **ADB** installed and on system PATH
4. **Eatventure** game installed on the device/emulator

> **Emulator limitation**: the bot runs fine against an Android Studio
> emulator, but Eatventure requires signing in through Google Play
> Games, and Google Play Games now blocks emulators from logging in.
> Without a login you cannot save/restore progress, so a real physical
> device is recommended for actual play.

## Quick Start

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Start emulator with Eatventure open, then (from the project root):
set PYTHONPATH=src
python -m auto_eatventure
```

Or use: `start.bat`

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Start emulator with Eatventure open, then (from the project root):
PYTHONPATH=src python3 -m auto_eatventure
```

Or use: `./start.sh`

## Environment Configuration

Copy `.env-sample` to `.env` and configure:

```bash
# Optional: target specific device (from `adb devices`)
device_serial=""

# Debug: log the score of every template check (very noisy)
DEBUG_TEMPLATE_MATCHING="0"

# Optional: override auto-computed template scale factor
TEMPLATE_SCALE_OVERRIDE=""

# Optional: "1" = select Popular Dish and stop it right away, only to
# complete the Masterchef "select a popular dish" quest. Default off.
POPULAR_DISH_ENABLED="0"

# Optional: "1" = accept the first Food Delivery order whenever one is
# available (mainly for the Food Delivery quest). Default off.
FOOD_DELIVERY_ENABLED="0"

# Optional: "0" = don't invite the first helper whenever one can be
# invited. Default on.
HELPER_INVITE_ENABLED="1"

# Optional: "0" = don't collect the free Adventures rewards after the
# start and every 5 hours. Default on.
COLLECT_ADVENTURES_ENABLED="1"

# Logging: console level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL="INFO"

# Logging: file level (written to logs/autoplay.log)
LOG_FILE_LEVEL="DEBUG"

# Logging: days to keep rotated log files
LOG_MAX_DAYS="7"
```

## Dependencies

From `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `adbutils` | >= 1.2.9 | ADB device control |
| `opencv-python` | >= 4.8.0 | Template matching |
| `numpy` | >= 1.26.0 | Array operations |
| `scikit-learn` | >= 1.3.0 | DBSCAN clustering |
| `Pillow` | >= 10.0.0 | Image capture/conversion |
| `python-dotenv` | >= 0.21.1 | `.env` file loading |

## Linting

Pylint configured via `.pylintrc`:
- 2-space indentation
- Max line length: 79 characters
- LF line endings
- `cv2.*` as generated members (compiled module)
- No docstring needed for functions shorter than 5 lines

```bash
pylint src/auto_eatventure
```

## Source File Layout

src layout with one package. Run everything from the project root
with `PYTHONPATH=src` (data paths like `matching_screenshots/`, `logs/`
and `.env` are relative to it).

```
src/auto_eatventure/
  __main__.py                # Entry point: python -m auto_eatventure
  main.py, game_loop.py, config.py, timer.py, logger.py
                             # Start-up, game loop, settings, timer, logging
  actions/                   # Game actions, one module per feature
  android/                   # ADB device layer
  vision/                    # Screenshot, template matching, colors, icons
  coords/                    # Reference positions, geometry, scaling
  sandbox.py                 # Interactive testing tool:
                             # PYTHONPATH=src python -m auto_eatventure.sandbox
```

See [Architecture](architecture.md) for the modules.
