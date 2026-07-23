"""
adb_autoplay.py - Main entry point and game loop

Orchestrates the game automation at the highest level.
All implementation details live in device.py,
template_matcher.py, and game_actions.py.
"""

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


class AutoEatventure:
  """Main bot orchestrator."""

  def __init__(self):
    self.device = Device()
    self.matcher = TemplateMatcher(self.device.sc)
    self.loc = Constants(self.device.sc)
    self.actions = GameActions(
      self.device, self.matcher, self.loc)

  def start_playing_game(self):
    """Main game loop — runs indefinitely."""
    count = 0
    swipe_count = 0
    nothing_to_update_count = 0
    new_level_started = True
    new_level_first_food_icon_swipe = False

    while True:
      count += 1

      swipe_count = self.actions.handle_stale_state(
        nothing_to_update_count, swipe_count)

      self.device.capture_screenshot()

      if count % 150 == 0:
        self.actions.close_accidental_popups()

      new_level_started = self.actions.try_upgrade_items(
        count, new_level_started)

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
      else:
        nothing_to_update_count += 1
        if count % 10 == 0:
          if self.actions.check_to_go_next_level():
            swipe_count = 0
            nothing_to_update_count = 0
            new_level_first_food_icon_swipe = False
            new_level_started = True


# ── Entry point ─────────────────────────────────────────────

bot = AutoEatventure()
bot.device.start_app()
bot.actions.init_game()
key_log.info("START - Bot started")
bot.start_playing_game()
