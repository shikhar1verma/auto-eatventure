"""Dialogs at the start of the bot: waiting until the game is ready,
closing dialogs that come late."""

import logging
import time

from auto_eatventure.actions import levels, popups, race_reward

log = logging.getLogger(__name__)

# Dialogs closed when the screen is dimmed, at most
DIMMING_DIALOG_CLOSE_TRIES = 5
# Start dialogs ("While you were away...", Offline Earnings) come when
# the server answers, up to ~30 s after the game is ready, and not on
# every start. The game loop doesn't wait for them, it checks its
# screenshot for them every 15 s during the first minute.
LATE_DIALOGS_CHECK_S = 15
LATE_DIALOGS_WATCH_S = 60


def wait_until_ready(game):
  """Wait until the game is playable.

  Taps known dialogs that can cover the screen when the bot is
  restarted, e.g. right after a renovation or a flight, and closes
  other dialogs by their red X (e.g. "While you were away...").
  Dialogs that come late are closed by LateDialogWatch.
  """
  while True:
    game.screen.capture()
    if game.screen.has('settings'):
      break
    if game.screen.has('offline_earnings'):
      game.device.tap(game.coords.close_offline_earnings)
      break
    if levels.is_welcome_okay_shown(game):
      log.info('Init: closing "Welcome to <city>" dialog')
      levels.tap_welcome_okay(game)
      continue
    if levels.is_open_button_shown(game):
      log.info('Init: tapping first stand "Open" button')
      levels.tap_open_button(game)
      continue
    if race_reward.claim(game):
      continue
    if popups.close_popup(game):
      continue
    log.info('Init: waiting for game to be ready')
    time.sleep(5)
  log.info('Init: game is ready')


def close_dimming_dialogs(game):
  """Close dialogs that dim the screen. Returns True when the screen
  is not dimmed."""
  # A dialog tapped just before may still be fading out
  time.sleep(1)
  game.screen.capture()
  for _ in range(DIMMING_DIALOG_CLOSE_TRIES):
    if not popups.is_screen_dimmed(game):
      return True
    if levels.is_welcome_okay_shown(game):
      log.info('Start: closing "Welcome to <city>" dialog')
      levels.tap_welcome_okay(game)
    elif levels.is_open_button_shown(game):
      log.info('Start: tapping first stand "Open" button')
      levels.tap_open_button(game)
    elif race_reward.claim(game):
      pass
    elif not popups.close_popup(game):
      # A tap outside a modal dialog closes it and doesn't reach the
      # restaurant behind it (Back doesn't close dialogs)
      log.info('Start: dimmed screen without a red X, tapping '
               'outside the dialog')
      game.device.tap(game.null_spot)
    time.sleep(1)
    game.screen.capture()
  return not popups.is_screen_dimmed(game)


class LateDialogWatch:
  """Closes start dialogs that come after wait_until_ready(), checked
  on the game loop's screenshot during the first minute."""

  def __init__(self):
    now = time.monotonic()
    self._end = now + LATE_DIALOGS_WATCH_S
    self._next_check = now + LATE_DIALOGS_CHECK_S

  def close_dialogs(self, game):
    """Close them when it's time for a check and the screen is dimmed.
    Returns True when the screen was dimmed."""
    if self._next_check > self._end or time.monotonic() < self._next_check:
      return False
    self._next_check = time.monotonic() + LATE_DIALOGS_CHECK_S
    if not popups.is_screen_dimmed(game):
      return False
    log.info('Late start dialog, closing it')
    close_dimming_dialogs(game)
    return True
