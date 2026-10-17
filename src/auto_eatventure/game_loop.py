"""GameLoop: the endless loop deciding what the bot does next."""

from auto_eatventure import config
from auto_eatventure.actions import (
  adventures, boxes, food_delivery, helper_invite, levels, popular_dish,
  popups, stations, upgrades)
from auto_eatventure.actions.stale import StaleWatch
from auto_eatventure.actions.start_dialogs import LateDialogWatch
from auto_eatventure.timer import Timer

# Every this many loops: popups closed, the next level checked (when
# there is no station to upgrade), boxes opened
POPUP_CHECK_LOOPS = 150
NEXT_LEVEL_CHECK_LOOPS = 10
BOX_CHECK_LOOPS = 2


class GameLoop:
  """Plays the game: one screenshot per loop, then the first thing to
  do on it."""

  def __init__(self, game):
    self.game = game
    self.loops = 0
    self.stale = StaleWatch()
    self.late_dialogs = LateDialogWatch()
    # The first station icons of a level move the restaurant into place
    self.needs_reposition = True
    self.popular_dish_timer = Timer()
    # After a level change no dish can be selected until the first
    # stand is open, i.e. until the first station upgrade
    self.popular_dish_waits_for_upgrade = False
    self.food_delivery_timer = Timer()
    self.helper_invite_timer = Timer()
    self.adventures_timer = Timer()

  def run(self):
    while True:
      self.play_once()

  def play_once(self):
    """One loop: a new screenshot and the actions it calls for. An
    action that changes the screen a lot ends the loop early."""
    game = self.game
    self.loops += 1
    self.stale.check(game)

    if (config.POPULAR_DISH_ENABLED
        and not self.popular_dish_waits_for_upgrade
        and self.popular_dish_timer.is_due()):
      self._select_popular_dish()
    if config.COLLECT_ADVENTURES_ENABLED and self.adventures_timer.is_due():
      self._collect_adventures()

    game.screen.capture()
    if self.late_dialogs.close_dialogs(game):
      return
    if (config.FOOD_DELIVERY_ENABLED and self.food_delivery_timer.is_due()
        and self._accept_food_delivery()):
      return
    if (config.HELPER_INVITE_ENABLED and self.helper_invite_timer.is_due()
        and self._invite_helper()):
      return

    if self.loops % POPUP_CHECK_LOOPS == 0:
      popups.close_popup(game)
    upgrades.buy_if_available(game)
    if self.loops == 1 or self.loops % BOX_CHECK_LOOPS == 0:
      boxes.open_all(game)

    icons = stations.find_icons(game)
    if icons:
      self._upgrade_stations(icons)
    else:
      self._no_station_to_upgrade()

  def _upgrade_stations(self, icons):
    if self.needs_reposition:
      stations.reposition_after_new_level(self.game, icons)
      self.needs_reposition = False
      return
    self.stale.found_work()
    if stations.scroll_if_icons_too_high(self.game, icons):
      return
    stations.upgrade(self.game, icons)
    if self.popular_dish_waits_for_upgrade:
      self.popular_dish_waits_for_upgrade = False
      self.popular_dish_timer.reset()

  def _no_station_to_upgrade(self):
    self.stale.found_nothing()
    if (self.loops % NEXT_LEVEL_CHECK_LOOPS == 0
        and levels.go_to_next_level(self.game)):
      self.stale.reset()
      self.needs_reposition = True
      self.popular_dish_waits_for_upgrade = True

  def _select_popular_dish(self):
    selected = popular_dish.select(self.game)
    self.popular_dish_timer.postpone(
      popular_dish.COOLDOWN_S if selected else popular_dish.RETRY_S)

  def _collect_adventures(self):
    finished = adventures.collect(self.game)
    self.adventures_timer.postpone(
      adventures.INTERVAL_S if finished else adventures.RETRY_S)

  def _accept_food_delivery(self):
    """Returns True when a delivery was available (and tried)."""
    truck = food_delivery.find_truck(self.game)
    if truck is None:
      return False
    food_delivery.accept(self.game, truck)
    self.food_delivery_timer.postpone(food_delivery.PAUSE_S)
    return True

  def _invite_helper(self):
    """Returns True when a helper was available (and tried)."""
    if not helper_invite.is_available(self.game):
      return False
    invited = helper_invite.invite(self.game)
    self.helper_invite_timer.postpone(
      helper_invite.PAUSE_S if invited else helper_invite.RETRY_S)
    return True
