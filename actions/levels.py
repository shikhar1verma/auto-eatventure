"""Next level: renovation, or a flight to the next city."""

import logging
import time

from actions import chests
from bot.logger import key_log

log = logging.getLogger(__name__)

# The "Welcome to <city>" dialog (Okay) appears after the flight
# animation (~15-19 s) and the "Open" dialog of the first stand after
# the renovate animation / Okay; both are slow on some phones. They
# are awaited up to this long; then tapped blindly (e.g. closed by
# hand).
WELCOME_OKAY_TIMEOUT_S = 60
OPEN_BUTTON_TIMEOUT_S = 45
# Delay before tapping, so the dialog finishes its pop-in animation
BUTTON_TAP_DELAY_S = 1
# The next level / next city icon of the button in the bottom left
NEXT_LEVEL_ICON_THRESHOLD = 0.95
DIALOG_BUTTON_THRESHOLD = 0.9


def go_to_next_level(game):
  """Renovate to the next level, or fly to the next city, when the
  game offers it. Returns True when the level changed."""
  screen = game.screen
  if screen.has('go_next_level_icon', threshold=NEXT_LEVEL_ICON_THRESHOLD):
    _renovate(game)
  elif screen.has('fly_next_city_icon',
                  threshold=NEXT_LEVEL_ICON_THRESHOLD):
    _fly_to_next_city(game)
  else:
    return False
  chests.open_all(game)
  return True


def is_welcome_okay_shown(game):
  """The "Welcome to <city>" dialog after a flight."""
  return game.screen.has(
    'welcome_city_okay', threshold=DIALOG_BUTTON_THRESHOLD)


def is_open_button_shown(game):
  """The "Open" dialog of the first stand on a new level."""
  return game.screen.has('open_button', threshold=DIALOG_BUTTON_THRESHOLD)


def tap_welcome_okay(game):
  """Wait for "Okay" of the "Welcome to <city>" dialog and tap it."""
  _wait_and_tap(game, 'Okay', is_welcome_okay_shown,
                game.coords.welcome_okay_button, WELCOME_OKAY_TIMEOUT_S)


def tap_open_button(game):
  """Wait for "Open" of the first stand and tap it."""
  _wait_and_tap(game, 'Open', is_open_button_shown,
                game.coords.first_stand_open_button,
                OPEN_BUTTON_TIMEOUT_S)


def _renovate(game):
  log.info('Renovating to next level')
  game.device.tap(game.coords.next_level_button)
  time.sleep(2)
  game.device.tap(game.coords.renovate_button)
  tap_open_button(game)
  key_log.info('NEXT LEVEL - Renovated to next level')


def _fly_to_next_city(game):
  game.device.tap(game.coords.next_level_button)
  time.sleep(2)
  log.info('Flying to next city')
  game.device.tap(game.coords.fly_next_city_button)
  tap_welcome_okay(game)
  tap_open_button(game)
  time.sleep(5)
  key_log.info('FLY - Flying to next city')


def _wait_and_tap(game, name, is_shown, button, timeout_s):
  """Wait for a dialog button and tap it.

  If it doesn't show up in time, tap its position anyway and log a
  warning, the bot then continues.
  """
  deadline = time.monotonic() + timeout_s
  while True:
    game.screen.capture()
    if is_shown(game):
      time.sleep(BUTTON_TAP_DELAY_S)
      break
    if time.monotonic() >= deadline:
      log.warning('%s button not found within %d s, tapping it blindly. '
                  'This should not normally happen.', name, timeout_s)
      key_log.warning('WARNING - %s button not found', name)
      break
    time.sleep(1)
  game.device.tap(button)
