"""Adventures (Zeus' Feast, Hangry Pirates): collecting the free
rewards with "Complete last level"."""

import logging
import time
from typing import NamedTuple

from auto_eatventure.actions import popups
from auto_eatventure.logger import key_log
from auto_eatventure.coords.geometry import Point
from auto_eatventure.vision.colors import RED

log = logging.getLogger(__name__)

# Keys refill about once a day, so the first collection runs right
# after the start and the next ones every 5 hours. A collection that
# hit an unexpected screen is retried sooner.
INTERVAL_S = 5 * 60 * 60
RETRY_S = 60 * 60


class Adventure(NamedTuple):
  """An adventure and its key icon templates."""
  name: str
  # Key icon in the "Events" list and in the level dialog's counter
  list_key: str
  dialog_key: str


# The counter shows a key while free runs are left and an ad icon
# (never tapped) when the keys are used up
ADVENTURES = (
  Adventure("Zeus' Feast",
            'adventure_zeus_key', 'adventure_zeus_dialog_key'),
  Adventure('Hangry Pirates',
            'adventure_pirates_key', 'adventure_pirates_dialog_key'),
)
# Key templates score 0.93-1.00, the other adventure's key and the ad
# icon <= 0.46
KEY_THRESHOLD = 0.8
# The red X of an open dialog fills ~75% of its area, <= 13% when the
# dialog is closed or covered; the reward summary's X ~89%, 0% before
CLOSE_RED_MIN_RATIO = 0.5
# Right arrow of the level dialog ~46% blue, 0% on the last level. The
# Events dialog has blue Enter buttons there, so it is checked only
# with the level dialog open.
ARROW_BLUE = [((95, 120, 150), (115, 255, 255))]
ARROW_MIN_RATIO = 0.2
# Background of the full screen reward cards, dark blue for Zeus'
# Feast, brown for Hangry Pirates: 100% in its empty area, <= 7% on
# the restaurant and the dialogs
REWARD_BACKGROUND = [((95, 200, 110), (105, 255, 150)),
                     ((16, 130, 140), (26, 185, 195))]
REWARD_BACKGROUND_MIN_RATIO = 0.8
# Time for the dialogs and reward screens to open / close
DIALOG_DELAY_S = 1.5
REVEAL_DELAY_S = 1.5
# The reward screen after "Complete last level" is awaited up to this
# long
REWARD_TIMEOUT_S = 10
# Safety limits: arrow taps to the last level, taps to reveal one
# run's cards (1 to ~10, one more shows the summary) and runs per
# adventure (bonus key cards add runs)
MAX_ARROW_TAPS = 30
MAX_REVEAL_TAPS = 15
MAX_RUNS = 10


def collect(game):
  """Collect the free Adventures rewards.

  Opens "Events" (party popper), scrolls to the Adventures at its
  bottom and, for each adventure with a key icon, completes its last
  level while the counter shows a key. An ad icon means the free runs
  are used up; it is never tapped. Returns False when a screen didn't
  show up as expected (the dialogs are then closed).
  """
  collected = {}
  finished = _collect_all(game, collected)
  if collected:
    key_log.info('ADVENTURES - Collected rewards: %s', ', '.join(
      f'{name} {runs}x' for name, runs in collected.items()))
  if not finished:
    _close_all_screens(game)
  return finished


def _collect_all(game, collected):
  """Collect all adventures; count the runs in collected
  {name: runs}."""
  device = game.device
  coords = game.coords
  game.screen.capture()
  if not game.screen.has('settings'):
    log.warning('Adventures: main screen not found')
    return False
  device.tap(coords.events_button)
  time.sleep(DIALOG_DELAY_S)
  game.screen.capture()
  if not _is_events_dialog_open(game):
    log.warning('Adventures: Events dialog not found')
    return False
  device.swipe(coords.events_scroll)
  time.sleep(DIALOG_DELAY_S)
  for adventure in ADVENTURES:
    game.screen.capture()
    if not _is_events_dialog_open(game):
      log.warning('Adventures: Events dialog not found')
      return False
    enter_button = _find_enter_button(game, adventure.list_key)
    if enter_button is None:
      log.info('Adventures: %s has no free run', adventure.name)
      continue
    device.tap(enter_button)
    time.sleep(DIALOG_DELAY_S)
    if not _complete_last_level(game, adventure, collected):
      return False
    log.info('Adventures: %s completed %dx',
             adventure.name, collected.get(adventure.name, 0))
    if not _close_dialog(game, _is_level_dialog_open,
                         coords.adventure_level_close):
      return False
  return _close_dialog(game, _is_events_dialog_open, coords.events_close)


def _complete_last_level(game, adventure, collected):
  """Complete the last level while the counter shows a key.

  Bonus key cards add runs, so the count is not known in advance.
  Every run is counted in collected. Returns False on an unexpected
  screen.
  """
  for _ in range(MAX_RUNS):
    game.screen.capture()
    if not _is_level_dialog_open(game):
      log.warning('Adventures: level dialog not found')
      return False
    if not _select_last_level(game):
      return False
    if not _has_key(game, adventure.dialog_key):
      return True
    game.device.tap(game.coords.adventure_complete_last)
    time.sleep(DIALOG_DELAY_S)
    if not _reveal_rewards(game):
      return False
    collected[adventure.name] = collected.get(adventure.name, 0) + 1
  return True


def _select_last_level(game):
  """Tap the right arrow until the last level is selected."""
  for _ in range(MAX_ARROW_TAPS):
    if not _has_right_arrow(game):
      return True
    game.device.tap(game.coords.adventure_right_arrow)
    time.sleep(DIALOG_DELAY_S)
    game.screen.capture()
  log.warning('Adventures: last level not reached')
  return False


def _reveal_rewards(game):
  """Tap the reward cards until the summary shows, then close it.

  Every tap is preceded by a check of the reward screen, so a tap
  never lands on anything else (e.g. an ad).
  """
  if not _wait_for_reward_screen(game):
    log.warning('Adventures: reward screen not found')
    return False
  for _ in range(MAX_REVEAL_TAPS):
    game.screen.capture()
    if not _is_reward_screen(game):
      log.warning('Adventures: reward screen not found')
      return False
    summary = _is_summary(game)
    # A tap reveals the next card, on the summary it closes it
    game.device.tap(game.coords.adventure_reveal_tap)
    time.sleep(REVEAL_DELAY_S)
    if summary:
      return True
  log.warning('Adventures: reward summary not found')
  return False


def _wait_for_reward_screen(game):
  """Wait for the reward screen after "Complete last level"."""
  deadline = time.monotonic() + REWARD_TIMEOUT_S
  while time.monotonic() < deadline:
    game.screen.capture()
    if _is_reward_screen(game):
      return True
    time.sleep(1)
  return False


def _close_dialog(game, is_open, close_button):
  """Tap the dialog's X if the dialog is open."""
  game.screen.capture()
  if not is_open(game):
    log.warning('Adventures: dialog to close not found')
    return False
  game.device.tap(close_button)
  time.sleep(DIALOG_DELAY_S)
  return True


def _close_all_screens(game):
  """Close the screens left open by a failed collection.

  The reward cards have no X: they are tapped through like in a run
  (each tap after a check of the reward screen), then the level and
  Events dialogs are closed by their red X.
  """
  for _ in range(MAX_REVEAL_TAPS + 1):
    game.screen.capture()
    if not _is_reward_screen(game):
      break
    game.device.tap(game.coords.adventure_reveal_tap)
    time.sleep(REVEAL_DELAY_S)
  for _ in range(3):
    game.screen.capture()
    if not popups.close_popup(game):
      return


# ── Detection ─────────────────────────────────────────────────────────

def _is_events_dialog_open(game):
  """The "Events" dialog (party popper) is open."""
  return _is_red_close(game, game.coords.events_close_roi)


def _is_level_dialog_open(game):
  """Level dialog of an adventure is open on top."""
  return _is_red_close(game, game.coords.adventure_level_close_roi)


def _is_summary(game):
  """Summary of the revealed reward cards (all cards revealed)."""
  return _is_red_close(game, game.coords.adventure_summary_close_roi)


def _is_red_close(game, region):
  """Red X of a dialog / reward summary in the region."""
  return game.screen.color_ratio(region, RED) >= CLOSE_RED_MIN_RATIO


def _is_reward_screen(game):
  """Full screen reward cards (revealing or the summary)."""
  return (game.screen.color_ratio(
            game.coords.adventure_reward_bg_roi, REWARD_BACKGROUND)
          >= REWARD_BACKGROUND_MIN_RATIO)


def _has_right_arrow(game):
  """Right arrow of the level dialog: the last level isn't selected."""
  return (game.screen.color_ratio(
            game.coords.adventure_right_arrow_roi, ARROW_BLUE)
          >= ARROW_MIN_RATIO)


def _find_enter_button(game, key_template):
  """Enter button of the adventure whose key icon is shown in the
  "Events" list (free runs left), else None."""
  coords = game.coords
  key = game.screen.find(key_template, coords.events_list_roi,
                         KEY_THRESHOLD)
  if key is None:
    return None
  return Point(key.center.x + coords.adventure_enter_offset_x,
               key.center.y + coords.adventure_enter_offset_y)


def _has_key(game, key_template):
  """Key icon on the level dialog's counter (an ad icon there means
  no free run)."""
  return game.screen.has(key_template, game.coords.adventure_counter_roi,
                         KEY_THRESHOLD)
