"""Upgrades dialog: buying upgrades while the upgrade button shows its
red badge."""

import logging
import time

from vision.colors import RED

log = logging.getLogger(__name__)

# The red badge pulses (size, tilt), which made template matching miss
# ~1/3 of the frames, so its red pixels are counted. It covers ~21-30%
# of its area, 0% when it is not shown; red food in customers' bubbles
# behind the area reached ~5%.
BADGE_MIN_RATIO = 0.12
# Buy button of the first row: blue while affordable, grey when not
# (bought upgrades leave the list, so the next one moves to the first
# row)
BUY_BLUE = [((95, 120, 200), (110, 255, 255))]
BUY_MIN_RATIO = 0.3
# The red X of the open dialog fills ~80% of its area, ~0-10% without
# the dialog
DIALOG_MIN_RATIO = 0.4
# Upgrades are bought in rounds of this many taps, each preceded by a
# check of the first row, up to MAX_TAPS (a new level)
TAPS_PER_CHECK = 5
MAX_TAPS = 50
# Time for a station popup to close after a tap on the null spot
STATION_POPUP_CLOSE_DELAY_S = 0.3
# Time for the dialog to pop in before the first check
DIALOG_OPEN_DELAY_S = 0.5
# The closed dialog fades out for ~0.6 s; a screenshot taken meanwhile
# hides the station icons (with the badge still shown, the next loops
# kept missing the stations and went stale)
DIALOG_CLOSE_DELAY_S = 0.8


def buy_if_available(game):
  """Buy upgrades when the upgrade button shows its badge.

  Checked on every loop screenshot, so upgrades are bought soon after
  they become affordable.
  """
  if not _has_badge(game):
    return
  log.info('Upgrades available — attempting to upgrade')
  _buy_upgrades(game)
  game.screen.capture()


def _buy_upgrades(game):
  """Open the dialog and buy the first row's upgrade while it is
  affordable, in rounds of TAPS_PER_CHECK taps."""
  device = game.device
  coords = game.coords
  # A station popup may still be open after stations.upgrade(); a tap
  # on the upgrade button would only close it
  device.tap(game.null_spot)
  time.sleep(STATION_POPUP_CLOSE_DELAY_S)
  device.tap(coords.upgrade_button)
  time.sleep(DIALOG_OPEN_DELAY_S)
  game.screen.capture()
  if not _is_dialog_open(game):
    # The close tap would land on the restaurant and could open a
    # station popup hiding the station icons, so tap the null spot
    log.info('Upgrades dialog did not open')
    device.tap(game.null_spot)
    time.sleep(DIALOG_CLOSE_DELAY_S)
    return
  taps = 0
  while taps < MAX_TAPS:
    if taps:
      game.screen.capture()
    if not _is_first_affordable(game):
      break
    for _ in range(TAPS_PER_CHECK):
      device.tap(coords.first_upgrade_buy)
      time.sleep(0.2)
    taps += TAPS_PER_CHECK
  log.info('Upgrade taps: %d', taps)
  device.tap(coords.close_upgrades)
  time.sleep(DIALOG_CLOSE_DELAY_S)


def _has_badge(game):
  return (game.screen.color_ratio(game.coords.upgrade_badge_roi, RED)
          >= BADGE_MIN_RATIO)


def _is_dialog_open(game):
  """Red X (close) of the Upgrades dialog is shown."""
  return (game.screen.color_ratio(game.coords.close_upgrades_roi, RED)
          >= DIALOG_MIN_RATIO)


def _is_first_affordable(game):
  """Blue buy button of the first row."""
  return (game.screen.color_ratio(
            game.coords.first_upgrade_buy_roi, BUY_BLUE)
          >= BUY_MIN_RATIO)
