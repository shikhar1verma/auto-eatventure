# Development Setup

> <- Back to [AGENTS.md](../../AGENTS.md)

## Prerequisites

1. **Python 3.10+** (uses `tuple[int, int]` type hints)
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
# Start emulator with Eatventure open, then:
python adb_autoplay.py
```

Or use: `start.bat`

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Start emulator with Eatventure open, then:
python3 adb_autoplay.py
```

Or use: `./start.sh`

## Environment Configuration

Copy `.env-sample` to `.env` and configure:

```bash
# Optional: target specific device (from `adb devices`)
device_serial=""

# Debug: print raw template matching values (very noisy)
DEBUG_TEMPLATE_MATCHING="0"

# Optional: override auto-computed template scale factor
TEMPLATE_SCALE_OVERRIDE=""

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

```bash
pylint adb_autoplay.py device.py template_matcher.py game_actions.py
```

## Source File Layout

```
adb_autoplay.py              # Entry point + game loop (~86 lines)
logger.py                    # Logging setup (~75 lines)
device.py                    # ADB device layer (~115 lines)
template_matcher.py          # OpenCV matching (~267 lines)
game_actions.py              # Game logic (~411 lines)
coords.py                    # Reference coordinates
scaled_coords.py             # Resolution scaling
constants.py                 # Coordinate dicts
```
