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
| `WARNING` | Recovery actions: stale state restart, missing config, invalid env values |
| `ERROR` | Failures: template not found, mask empty (used in debug scripts) |

## Usage in Code

```python
from logger import get_logger

log = get_logger(__name__)

log.debug('Upgrading items')
log.info('Chest found — opening.')
log.warning('Nothing to update — restarting app.')
```

## Initialization

`setup_logging()` must be called once at startup, after `load_dotenv()`:

```python
from dotenv import load_dotenv
load_dotenv()

from logger import setup_logging
setup_logging()
```

This is done in `adb_autoplay.py` (the entry point).

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
| `RESTART` | Stale state triggers app restart | `RESTART - Stale state, restarting app` |

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
2024-01-15 09:01:55,234  RESTART - Stale state, restarting app
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
