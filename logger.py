"""
logger.py - Centralized logging configuration

Configures Python's logging module with:
- Console handler: prints to stdout (default level: INFO)
- File handler: writes to logs/ directory with daily rotation
- Key events file: important milestones only (logs/key_events.log)

Configuration via environment variables:
- LOG_LEVEL: console log level (default "INFO")
- LOG_FILE_LEVEL: file log level (default "DEBUG")
- LOG_MAX_DAYS: days to keep rotated log files (default 7)
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "autoplay.log")
KEY_EVENTS_FILE = os.path.join(LOG_DIR, "key_events.log")

# Format for console: match previous print() style
CONSOLE_FORMAT = "%(message)s"
# Format for file: include timestamp, level, module
FILE_FORMAT = (
  "%(asctime)s [%(levelname)-5s] %(name)s: %(message)s")
# Format for key events: timestamp + message only
KEY_EVENTS_FORMAT = "%(asctime)s  %(message)s"


def setup_logging():
  """Initialize logging with console and file handlers.

  Call once at application startup (before any logger usage).
  """
  console_level = os.getenv("LOG_LEVEL", "INFO").upper()
  file_level = os.getenv("LOG_FILE_LEVEL", "DEBUG").upper()
  max_days = int(os.getenv("LOG_MAX_DAYS", "30"))

  os.makedirs(LOG_DIR, exist_ok=True)

  root = logging.getLogger()
  root.setLevel(logging.DEBUG)

  # Remove existing handlers (avoid duplicates on re-init)
  root.handlers.clear()

  # Console handler
  console_handler = logging.StreamHandler()
  console_handler.setLevel(getattr(logging, console_level,
                                   logging.INFO))
  console_handler.setFormatter(
    logging.Formatter(CONSOLE_FORMAT))
  root.addHandler(console_handler)

  # File handler with daily rotation
  file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=max_days,
    encoding="utf-8")
  file_handler.setLevel(getattr(logging, file_level,
                                logging.DEBUG))
  file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
  file_handler.suffix = "%Y-%m-%d"
  root.addHandler(file_handler)

  # Key events logger (separate file, no console output)
  _setup_key_events_logger(max_days)


def _setup_key_events_logger(max_days):
  """Configure the dedicated key events logger."""
  key_logger = logging.getLogger("key_events")
  key_logger.propagate = False
  key_logger.setLevel(logging.INFO)
  key_logger.handlers.clear()

  handler = TimedRotatingFileHandler(
    KEY_EVENTS_FILE,
    when="midnight",
    interval=1,
    backupCount=max_days,
    encoding="utf-8")
  handler.setLevel(logging.INFO)
  handler.setFormatter(
    logging.Formatter(KEY_EVENTS_FORMAT))
  handler.suffix = "%Y-%m-%d"
  key_logger.addHandler(handler)


def get_logger(name):
  """Get a named logger for a module.

  Usage:
    from logger import get_logger
    log = get_logger(__name__)
    log.info("Something happened")
  """
  return logging.getLogger(name)


def get_key_logger():
  """Get the key events logger.

  Writes only to logs/key_events.log (no console output).
  Use for key milestones: level transitions, restarts, etc.

  Usage:
    from logger import get_key_logger
    key_log = get_key_logger()
    key_log.info("FLY - Flying to next city")
  """
  return logging.getLogger("key_events")
