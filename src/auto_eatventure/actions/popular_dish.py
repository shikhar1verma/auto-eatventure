"""Popular Dish skill: selected (and stopped right away) only for the
Masterchef quest."""

import logging
import time

from auto_eatventure.actions import popups
from auto_eatventure.logger import key_log

log = logging.getLogger(__name__)

# Popular Dish cooldown is ~10 min (reset by renovation / new city).
# After a level change no dish can be selected until the first stand
# is open, so the game loop waits for the first station upgrade.
# Failed attempts are retried sooner.
COOLDOWN_S = 10 * 60 + 30
RETRY_S = 60

# Time for the Active Skills / Select a dish dialogs to animate
DIALOG_DELAY_S = 1.5

# States of the Popular Dish row button and their templates
BUTTON_TEMPLATES = {
  'select': 'popular_dish_select',
  'start': 'popular_dish_start',
  'stop': 'popular_dish_stop',
}
BUTTON_THRESHOLD = 0.9


def select(game):
  """Select the first dish as Popular Dish, start the skill and stop
  it right away.

  The skill effect is not used, only the selection counts for the
  Masterchef quest. Returns True when the skill was stopped, i.e. its
  cooldown has started.
  """
  # The button goes select -> start -> stop -> grey (cooldown). Each
  # step continues from the state found, so an attempt interrupted
  # earlier is finished as well.
  state = _tap_and_get_button_state(game, game.coords.skills_circle)
  if state == 'select':
    state = _choose_first_dish(game)
  if state == 'start':
    state = _tap_and_get_button_state(
      game, game.coords.popular_dish_button)
  stopped = False
  if state == 'stop':
    stopped = _tap_and_get_button_state(
      game, game.coords.popular_dish_button) is None

  if stopped:
    log.info('Popular Dish selected and stopped')
    key_log.info('POPULAR DISH - Selected first dish')
  else:
    log.info('Popular Dish not selected (button: %s)', state)
  _close_skill_dialogs(game)
  return stopped


def _choose_first_dish(game):
  """Open "Select a dish" and tap the first selectable dish.

  Returns the button state afterwards, 'start' when a dish was chosen.
  """
  game.device.tap(game.coords.popular_dish_button)
  time.sleep(DIALOG_DELAY_S)
  for dish in game.coords.first_dish_candidates:
    state = _tap_and_get_button_state(game, dish)
    if state == 'start':
      return state
  log.info('No dish to select yet (no stand open)')
  return None


def _tap_and_get_button_state(game, point):
  game.device.tap(point)
  time.sleep(DIALOG_DELAY_S)
  game.screen.capture()
  return _button_state(game)


def _button_state(game):
  """'select', 'start', 'stop' or None (grey cooldown button / dialog
  not open) of the Popular Dish row button."""
  for state, template in BUTTON_TEMPLATES.items():
    if game.screen.has(template, game.coords.popular_dish_button_roi,
                       BUTTON_THRESHOLD):
      return state
  return None


def _close_skill_dialogs(game):
  """Close "Select a dish" and "Active Skills" if open."""
  game.screen.capture()
  for _ in range(2):
    if not popups.close_popup(game):
      break
