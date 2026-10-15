# Logging

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The project uses Python's built-in `logging` module configured in `logger.py`. All output goes through structured loggers instead of raw `print()` calls.

## Architecture

```
logger.py              # setup_logging() + get_logger() + get_key_logger()
  |
  +-- Console handler  # StreamHandler -> stdout (default: INFO)
  |
  +-- File handler     # TimedRotatingFileHandler -> logs/autoplay.log
  |                    # Rotates daily, keeps LOG_MAX_DAYS backups
  |
  +-- Key events       # TimedRotatingFileHandler -> logs/key_events.log
                       # Key milestones only (file-only, no console)
```

## Configuration (via `.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | `INFO` | Console output verbosity |
| `LOG_FILE_LEVEL` | `DEBUG` | File output verbosity |
| `LOG_MAX_DAYS` | `7` | Days to retain rotated log files |

## Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Internal details: raw template match scores, pixel checks |
| `INFO` | All game actions: upgrading station, opening boxes, food upgrades, chests, level transitions, ads, layout adjustments, stale swipes |
| `WARNING` | Recovery actions: stale state (bring game to foreground), missing config, invalid env values |
| `ERROR` | Failures: template not found, mask empty (used in debug scripts); a crash (uncaught exception) with its traceback |

## Crashes

`setup_logging()` sets `sys.excepthook`, so an uncaught exception
(e.g. an ADB command failing after the phone got disconnected) is
logged as `Bot crashed` with its traceback to `autoplay.log` (and the
console) and as one short line to `key_events.log`. Before, the
traceback went only to the console window and the logs just stopped.
Ctrl+C (`KeyboardInterrupt`) is not logged as a crash.

## Usage in Code

```python
from logger import get_logger

log = get_logger(__name__)

log.debug('Upgrading items')
log.info('Chest found — opening.')
log.warning('Nothing to update — bringing game to foreground.')
```

## Initialization

`setup_logging()` must be called once at startup, after `load_dotenv()`:

```python
from dotenv import load_dotenv
load_dotenv()

from logger import setup_logging
setup_logging()
```

This is done in `adb_autoplay.py` (the entry point). Its first log
line is `START - Bot started`, so every bot start is easy to find
in `autoplay.log` (the key events log gets its own `START` entry
once the game is initialized).

## File Output

- Log directory: `logs/` (auto-created, gitignored)
- Active log file: `logs/autoplay.log`
- Rotated files: `logs/autoplay.log.YYYY-MM-DD`
- Rotation: daily at midnight
- Retention: configurable via `LOG_MAX_DAYS`

## Key Events Log

A separate file recording only key milestones. Useful for tracking progress (e.g. counting cleared restaurants).

- File: `logs/key_events.log`
- Rotated daily (same retention as main log)
- **No console output** — file only
- Format: `2024-01-15 14:23:01,234  EVENT_TYPE - description`

### Events recorded:

| Event | When | Message |
|-------|------|---------|
| `START` | Bot process begins | `START - Bot started` |
| `NEXT LEVEL` | Renovated to next level (same city) | `NEXT LEVEL - Renovated to next level` |
| `FLY` | Flying to a new city/restaurant | `FLY - Flying to next city` |
| `STALE` | Nothing to update for more than 50 loops, game brought to the foreground (not restarted; at most once per ~2-3 min) | `STALE - Nothing to update, bringing game to foreground` |
| `POPULAR DISH` | Popular Dish selected and stopped (optional) | `POPULAR DISH - Selected first dish` |
| `ADVENTURES` | Free Adventures rewards collected (only when something was collected) | `ADVENTURES - Collected rewards: Zeus' Feast 2x, Hangry Pirates 1x` |
| `WARNING` | First stand's "Open" button not found after renovate / fly (should not normally happen) | `WARNING - Open button not found` |
| `WARNING` | "Welcome to <city>" dialog's "Okay" button not found after fly (should not normally happen) | `WARNING - Okay button not found` |
| `ERROR` | Top bar line not found at start, the null spot stays at the fallback from `coords.py`; the search must be fixed for this phone | `ERROR - Top bar not found (<reason>), null spot at fallback (x, y), popups may stay open or an ad may start; fix place_null_click_below_top_bar()` |
| `ERROR` | The bot crashed (uncaught exception, e.g. the phone got disconnected); the traceback is in `autoplay.log` | `ERROR - Bot crashed: <exception type>, see autoplay.log` |

### Usage:

```python
from logger import get_key_logger

key_log = get_key_logger()
key_log.info("FLY - Flying to next city")
```

### Example output (`logs/key_events.log`):

```
2024-01-15 08:00:12,001  START - Bot started
2024-01-15 08:05:44,321  NEXT LEVEL - Renovated to next level
2024-01-15 08:12:01,456  NEXT LEVEL - Renovated to next level
2024-01-15 08:19:33,789  FLY - Flying to next city
2024-01-15 08:25:11,012  NEXT LEVEL - Renovated to next level
2024-01-15 09:01:55,234  STALE - Nothing to update, bringing game to foreground
```

## Console Output Format

```
<message>
```

Console format matches previous `print()` output (message only, no timestamps). This keeps the terminal clean during normal operation.

## File Output Format

```
2024-01-15 14:23:01,234 [INFO ] game_actions: Chest found — opening.
```

File format includes timestamp, level, and module name for debugging.

## Adding Log Statements

1. Import the logger at module top: `from logger import get_logger`
2. Create module logger: `log = get_logger(__name__)`
3. Use appropriate level: `log.debug()`, `log.info()`, `log.warning()`, `log.error()`
4. Use `%s`-style formatting (not f-strings) in log calls for lazy evaluation:
   ```python
   log.info('Found %d matches at (%d, %d)', count, x, y)
   ```

## Rules

- Never use `print()` in core modules (`adb_autoplay.py`, `device.py`, `template_matcher.py`, `game_actions.py`).
- Experimental scripts and `sandbox.py` may still use `print()` for interactive CLI output.
- Default console level (`INFO`) produces the same output users saw before the migration.
- Increase to `DEBUG` only when troubleshooting specific issues.
- Key game milestones must also be logged via `get_key_logger()` for progress tracking.
- Key event messages follow the pattern: `EVENT_TYPE - description`.
