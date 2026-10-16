"""Stale game: nothing to upgrade for many loops."""

import logging
import time

from actions import popups, race_reward
from bot.logger import key_log

log = logging.getLogger(__name__)

# Loops without a station to upgrade before the game is brought to the
# foreground (e.g. an ad or a dialog may block it)
RECOVERY_LOOPS = 50
# Loops without a station to upgrade before the restaurant is scrolled
# to search for stations, then every SEARCH_SWIPE_EVERY loops
SEARCH_SWIPE_LOOPS = 15
SEARCH_SWIPE_EVERY = 5
# Number of consecutive swipes in the same direction before reversing.
# Kept high enough that repeats * swipe distance (650px) still covers
# the same total travel as the old single 1285px swipe used to, so a
# full stale-swipe cycle still reaches the top/bottom of a tall level.
SWIPES_PER_DIRECTION = 7
# Red X popups closed at most when recovering (stacked dialogs)
RECOVERY_POPUP_CLOSE_TRIES = 3


class StaleWatch:
  """Counts the loops without a station to upgrade and acts on them."""

  def __init__(self):
    self.idle_loops = 0
    self._swipes = 0

  def found_work(self):
    self.idle_loops = 0

  def found_nothing(self):
    self.idle_loops += 1

  def reset(self):
    """Start over, e.g. on a new level."""
    self.idle_loops = 0
    self._swipes = 0

  def check(self, game):
    """Recover the game or scroll the restaurant when idle too long.

    Recovery happens once per RECOVERY_LOOPS idle loops, not on every
    loop until something can be upgraded.
    """
    if self.idle_loops > RECOVERY_LOOPS:
      self._recover(game)
      self.idle_loops = 0
    if (self.idle_loops >= SEARCH_SWIPE_LOOPS
        and self.idle_loops % SEARCH_SWIPE_EVERY == 0):
      self._search_swipe(game)

  def _recover(self, game):
    """Bring the game to the foreground and close blocking dialogs.

    The game is not restarted: start_app() only brings the running
    game to the foreground.
    """
    log.warning('Nothing to update for %d loops — bringing game to '
                'foreground.', self.idle_loops)
    key_log.info('STALE - Nothing to update, bringing game to foreground')
    game.device.start_app()
    time.sleep(1)
    # A dialog may block the game, e.g. one that came late at start or
    # "Restaurant Race ended!" (no X)
    game.screen.capture()
    race_reward.claim(game)
    for _ in range(RECOVERY_POPUP_CLOSE_TRIES):
      if not popups.close_popup(game):
        break
      # The race dialog may have been under the closed popup
      race_reward.claim(game)
    game.device.tap(game.null_spot)
    time.sleep(1)

  def _search_swipe(self, game):
    """Scroll the restaurant down, later up, to search for stations."""
    cycle_position = self._swipes % (SWIPES_PER_DIRECTION * 2)
    if cycle_position < SWIPES_PER_DIRECTION:
      swipe = game.coords.swipe_down
    else:
      swipe = game.coords.swipe_up
    log.info('Stale swipe — scrolling to find items')
    game.device.swipe(swipe)
    time.sleep(3)
    self._swipes += 1
