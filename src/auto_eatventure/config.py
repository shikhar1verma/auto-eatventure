"""Settings from the environment and the .env file (see .env-sample)."""

import os

from dotenv import load_dotenv

load_dotenv()


def _text(name, default=''):
  return os.getenv(name, default).strip()


def _flag(name, default):
  """A "1" / "0" switch."""
  return _text(name, default) == '1'


# ADB serial of the phone; empty = the first connected one
DEVICE_SERIAL = _text('device_serial')

# Optional features, see .env-sample
POPULAR_DISH_ENABLED = _flag('POPULAR_DISH_ENABLED', '0')
FOOD_DELIVERY_ENABLED = _flag('FOOD_DELIVERY_ENABLED', '0')
HELPER_INVITE_ENABLED = _flag('HELPER_INVITE_ENABLED', '1')
COLLECT_ADVENTURES_ENABLED = _flag('COLLECT_ADVENTURES_ENABLED', '1')

# Troubleshooting of the template detection
DEBUG_TEMPLATE_MATCHING = _flag('DEBUG_TEMPLATE_MATCHING', '0')
# A number replacing the resolution-based template scale; empty = off
TEMPLATE_SCALE_OVERRIDE = _text('TEMPLATE_SCALE_OVERRIDE')

LOG_LEVEL = _text('LOG_LEVEL', 'INFO')
LOG_FILE_LEVEL = _text('LOG_FILE_LEVEL', 'DEBUG')
LOG_MAX_DAYS = int(_text('LOG_MAX_DAYS', '30'))
