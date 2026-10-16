"""Dialogs covering the restaurant: popups with a red X, dimmed
screen."""

import logging
import time

log = logging.getLogger(__name__)

# The white settings gear (top right) has max brightness 255 on the
# restaurant, 2-11 under a dialog and 160-236 while a dialog animates.
# Station popups don't dim it.
SETTINGS_GEAR_MIN_BRIGHTNESS = 200


def close_popup(game):
  """Close a popup by its red X. Returns True when one was closed."""
  cross = game.screen.find('popup_close_cross')
  if cross is None:
    return False
  log.info('Popup detected — closing at (%d, %d)', *cross.center)
  game.device.tap(cross.center)
  time.sleep(1)
  game.screen.capture()
  return True


def is_screen_dimmed(game):
  """A dialog dims the white settings gear."""
  gear = game.coords.settings_roi.crop(game.screen.gray)
  return gear.max() < SETTINGS_GEAR_MIN_BRIGHTNESS
