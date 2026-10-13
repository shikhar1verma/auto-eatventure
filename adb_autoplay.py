"""
adb_autoplay.py - Main entry point and game loop

Orchestrates the game automation at the highest level.
All implementation details live in device.py,
template_matcher.py, and game_actions.py.
"""

import os
import time
import random

from dotenv import load_dotenv

load_dotenv()

from logger import setup_logging, get_logger, get_key_logger
from constants import Constants
from device import Device
from template_matcher import TemplateMatcher
from game_actions import GameActions

setup_logging()
log = get_logger(__name__)
key_log = get_key_logger()

# Optional: select the Popular Dish skill (and stop it right away)
# only to farm the Masterchef quest for selecting a popular dish.
# Off by default, it has no gameplay benefit.
POPULAR_DISH_ENABLED = os.getenv(
  "POPULAR_DISH_ENABLED", "0").strip() == "1"

# Popular Dish cooldown is ~10 min (reset by renovation / new city).
# After a level change no dish can be selected until the first stand
# is open, so the bot waits for the first food upgrade. Failed
# attempts are retried sooner.
POPULAR_DISH_COOLDOWN_S = 10 * 60 + 30
POPULAR_DISH_RETRY_S = 60

# Optional: accept the first Food Delivery order whenever one is
# available, mainly to complete a quest. Off by default.
FOOD_DELIVERY_ENABLED = os.getenv(
  "FOOD_DELIVERY_ENABLED", "0").strip() == "1"

# Availability is checked on the loop screenshot (cheap). After any
# attempt the checks pause, so a failure that leaves the truck
# available can't make the bot tap it in a tight loop. A delivery and
# its cooldown take longer than the pause anyway.
FOOD_DELIVERY_PAUSE_S = 60

# Optional: invite the first helper whenever one can be invited. On by
# default.
HELPER_INVITE_ENABLED = os.getenv(
  "HELPER_INVITE_ENABLED", "1").strip() == "1"

# Same pause as for Food Delivery. A helper works ~4 min and the
# cooldown is ~30 min, so it never delays a real invite. A failed
# attempt costs up to ~15 s (the list may not load at all, e.g.
# offline), so it is retried much later.
HELPER_INVITE_PAUSE_S = 60
HELPER_INVITE_RETRY_S = 10 * 60


class AutoEatventure:
  """Main bot orchestrator."""

  def __init__(self):
    self.device = Device()
    self.matcher = TemplateMatcher(self.device.sc)
    self.loc = Constants(self.device.sc)
    self.actions = GameActions(
      self.device, self.matcher, self.loc)

  def _select_popular_dish(self):
    """Select Popular Dish; return the time of the next try."""
    delay = (POPULAR_DISH_COOLDOWN_S
             if self.actions.select_popular_dish()
             else POPULAR_DISH_RETRY_S)
    return time.monotonic() + delay

  def _invite_helper(self):
    """Invite a helper; return the time of the next try."""
    delay = (HELPER_INVITE_PAUSE_S
             if self.actions.invite_helper()
             else HELPER_INVITE_RETRY_S)
    return time.monotonic() + delay

  def start_playing_game(self):
    """Main game loop — runs indefinitely."""
    count = 0
    swipe_count = 0
    nothing_to_update_count = 0
    new_level_first_food_icon_swipe = False
    popular_dish_next_try = 0
    popular_dish_wait_for_upgrade = False
    food_delivery_next_try = 0
    helper_invite_next_try = 0

    while True:
      count += 1

      nothing_to_update_count, swipe_count = (
        self.actions.handle_stale_state(
          nothing_to_update_count, swipe_count))

      if (POPULAR_DISH_ENABLED
          and not popular_dish_wait_for_upgrade
          and time.monotonic() >= popular_dish_next_try):
        popular_dish_next_try = self._select_popular_dish()

      self.device.capture_screenshot()

      if (FOOD_DELIVERY_ENABLED
          and time.monotonic() >= food_delivery_next_try):
        truck_coords = self.actions.get_food_delivery_truck_coords()
        if truck_coords:
          self.actions.accept_food_delivery(truck_coords)
          food_delivery_next_try = (
            time.monotonic() + FOOD_DELIVERY_PAUSE_S)
          continue

      if (HELPER_INVITE_ENABLED
          and time.monotonic() >= helper_invite_next_try
          and self.actions.is_having_helper_available()):
        helper_invite_next_try = self._invite_helper()
        continue

      if count % 150 == 0:
        self.actions.close_accidental_popups()

      self.actions.try_upgrade_items()

      if count == 1 or count % 2 == 0:
        self.actions.open_boxes()

      food_icons = self.actions.get_food_icon_locations()

      if food_icons and not new_level_first_food_icon_swipe:
        self.actions.reposition_after_new_level(food_icons)
        new_level_first_food_icon_swipe = True
        continue

      if food_icons:
        nothing_to_update_count = 0
        if self.actions.adjust_layout_if_icons_too_high(
            food_icons):
          continue
        random.shuffle(food_icons)
        self.actions.upgrade_food_items(food_icons)
        if popular_dish_wait_for_upgrade:
          popular_dish_wait_for_upgrade = False
          popular_dish_next_try = 0
      else:
        nothing_to_update_count += 1
        if count % 10 == 0:
          if self.actions.check_to_go_next_level():
            swipe_count = 0
            nothing_to_update_count = 0
            new_level_first_food_icon_swipe = False
            popular_dish_wait_for_upgrade = True


# ── Entry point ─────────────────────────────────────────────

log.info('START - Bot started')
bot = AutoEatventure()
bot.device.start_app()
bot.actions.init_game()
bot.actions.place_null_click_below_top_bar()
key_log.info("START - Bot started")
log.info('Popular Dish selection: %s',
         'enabled' if POPULAR_DISH_ENABLED else 'disabled')
log.info('Food Delivery: %s',
         'enabled' if FOOD_DELIVERY_ENABLED else 'disabled')
log.info('Helper invite: %s',
         'enabled' if HELPER_INVITE_ENABLED else 'disabled')
bot.start_playing_game()
