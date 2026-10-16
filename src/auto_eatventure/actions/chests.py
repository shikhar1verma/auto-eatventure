"""Chests given for a new level."""

import logging
import time

log = logging.getLogger(__name__)

# Taps on an open chest that take out its rewards
REWARD_TAPS = 3


def open_all(game):
  """Open the chests one by one while the chest icon is shown."""
  device = game.device
  coords = game.coords
  while True:
    log.info('Checking for chests')
    time.sleep(1)
    game.screen.capture()
    time.sleep(1)
    if not game.screen.has('chest_icon'):
      return
    log.info('Chest found — opening')
    device.tap(coords.chest)
    time.sleep(2)
    for _ in range(REWARD_TAPS):
      device.tap(coords.chest)
      time.sleep(1)
    device.tap(coords.close_chest)
    time.sleep(1)
