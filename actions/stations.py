"""Stations: finding their upgrade icons, upgrading them and scrolling
the restaurant to them."""

import logging
import random
import time

from coords.geometry import Point, Swipe
from vision.upgrade_icons import find_upgrade_icons

log = logging.getLogger(__name__)

# Stations upgraded in one loop, at most
STATIONS_PER_LOOP = 3
BETTER_FOOD_HOLD_MS = 3000


def find_icons(game):
  """Points of the station upgrade icons that can be tapped (none on
  a screen dimmed by a dialog)."""
  coords = game.coords
  icons = find_upgrade_icons(
    game.screen.hsv, coords.upgrade_arrow_min_height_y,
    coords.upgrade_arrow_max_height_y)
  return [icon for icon in icons
          if icon.y <= coords.station_icon_max_y
          and not _is_near_club_button(coords, icon)]


def upgrade(game, icons):
  """Upgrade up to STATIONS_PER_LOOP stations, picked at random."""
  coords = game.coords
  icons = random.sample(icons, len(icons))
  for icon in icons[:STATIONS_PER_LOOP]:
    log.info('Upgrading food item at (%d, %d)', *icon)
    game.device.tap(Point(
      icon.x + coords.station_tap_shift_x,
      icon.y + coords.station_tap_offset_y + coords.station_tap_shift_y))
    time.sleep(0.2)

    hold = Point(
      _away_from_side_buttons(
        coords, icon.x + coords.better_food_hold_offset_x),
      icon.y - coords.better_food_hold_offset_y)
    game.device.long_press(hold, BETTER_FOOD_HOLD_MS)
    time.sleep(0.4)

    if icon.y < coords.station_icon_tooltip_y:
      game.device.tap(Point(
        _away_from_side_buttons(
          coords, icon.x - coords.better_food_tap_offset_x),
        icon.y + coords.station_tap_offset_y))
    else:
      game.device.tap(game.null_spot)
    time.sleep(0.2)


def reposition_after_new_level(game, icons):
  """Swipe the topmost icon down to the tooltip boundary.

  Called once after a new level starts, when icons are first found.
  """
  log.info('Repositioning layout after new level')
  top_icon = min(icons, key=lambda icon: icon.y)
  game.device.swipe(Swipe(
    top_icon, Point(top_icon.x, game.coords.station_icon_tooltip_y)))
  time.sleep(3)
  game.device.start_app()
  time.sleep(3)
  game.screen.capture()


def scroll_if_icons_too_high(game, icons):
  """Swipe up a little when an icon is too close to the top.

  Returns True when the restaurant was scrolled (the icons moved).
  """
  if all(icon.y > game.coords.station_icon_min_y for icon in icons):
    return False
  log.info('Adjusting layout — icons too high')
  game.device.swipe(game.coords.swipe_little_up)
  time.sleep(3)
  game.device.start_app()
  time.sleep(1)
  game.screen.capture()
  return True


def _is_near_club_button(coords, icon):
  """Whether the icon's station box would overlap the club button
  (bottom-left corner), so it couldn't be opened."""
  return (icon.x < coords.side_button_zone_width_x
          and icon.y > coords.club_button_zone_top_y)


def _away_from_side_buttons(coords, x):
  """Nudge x toward the center, away from the side UI buttons
  (restaurant race, food boxes, etc.) pinned to the screen edges."""
  margin = coords.side_button_zone_width_x
  return max(margin, min(x, coords.screen_width - margin))
