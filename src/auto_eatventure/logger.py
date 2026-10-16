"""Logging to the console and to daily rotated files in logs/.

- Console: INFO and up by default
- logs/autoplay.log: everything (DEBUG) by default
- logs/key_events.log: key milestones only, via key_log (no console)
- Uncaught exceptions (crashes) and the end of the bot (Ctrl+C,
  closed window, kill) go to both log files
"""

import logging
import os
import signal
import sys
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'autoplay.log')
KEY_EVENTS_FILE = os.path.join(LOG_DIR, 'key_events.log')

CONSOLE_FORMAT = '%(message)s'
FILE_FORMAT = '%(asctime)s [%(levelname)-5s] %(name)s: %(message)s'
KEY_EVENTS_FORMAT = '%(asctime)s  %(message)s'

# Key milestones only (start, level changes, collected rewards,
# errors); details go to autoplay.log
key_log = logging.getLogger('key_events')
key_log.propagate = False


def setup_logging(console_level, file_level, max_days):
  """Set up the handlers. Call once at start, before logging."""
  os.makedirs(LOG_DIR, exist_ok=True)

  root = logging.getLogger()
  root.setLevel(logging.DEBUG)
  root.handlers.clear()

  console = logging.StreamHandler()
  console.setLevel(_level(console_level, logging.INFO))
  console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
  root.addHandler(console)

  root.addHandler(_daily_file_handler(
    LOG_FILE, _level(file_level, logging.DEBUG), FILE_FORMAT, max_days))

  key_log.setLevel(logging.INFO)
  key_log.handlers.clear()
  key_log.addHandler(_daily_file_handler(
    KEY_EVENTS_FILE, logging.INFO, KEY_EVENTS_FORMAT, max_days))

  sys.excepthook = _log_crash
  # Closed console window (SIGHUP, not on Windows) and kill (SIGTERM)
  # end the bot without an exception
  for name in ('SIGTERM', 'SIGHUP'):
    if hasattr(signal, name):
      signal.signal(getattr(signal, name), _log_stop)


def _level(name, default):
  return getattr(logging, name.upper(), default)


def _daily_file_handler(path, level, log_format, max_days):
  handler = TimedRotatingFileHandler(
    path, when='midnight', interval=1, backupCount=max_days,
    encoding='utf-8')
  handler.setLevel(level)
  handler.setFormatter(logging.Formatter(log_format))
  handler.suffix = '%Y-%m-%d'
  return handler


def _log_stop(signum, _frame):
  """Log the end of the bot by a signal, then exit."""
  _log_end(signal.Signals(signum).name)
  sys.exit(0)


def _log_end(reason):
  logging.getLogger(__name__).info('Bot stopped (%s)', reason)
  key_log.info('STOP - Bot stopped (%s)', reason)


def _log_crash(exc_type, exc_value, exc_traceback):
  """Log an uncaught exception, e.g. when the phone gets
  disconnected.

  Without this its traceback goes only to the console window. The full
  traceback goes to autoplay.log, one short line to key_events.log.
  Ctrl+C is logged as the end of the bot, not as a crash.
  """
  if issubclass(exc_type, KeyboardInterrupt):
    _log_end('Ctrl+C')
    return
  logging.getLogger(__name__).error(
    'Bot crashed', exc_info=(exc_type, exc_value, exc_traceback))
  key_log.error('ERROR - Bot crashed: %s, see autoplay.log',
                exc_type.__name__)
