"""Food Delivery: accepting the first order, mainly for a quest."""

import logging
import time

from auto_eatventure.actions import popups
from auto_eatventure.coords.geometry import Point

log = logging.getLogger(__name__)

# Availability is checked on the loop screenshot (cheap). After any
# attempt the checks pause, so a failure that leaves the truck
# available can't make the bot tap it in a tight loop. A delivery and
# its cooldown take longer than the pause anyway.
PAUSE_S = 60

# Time for the Food Delivery dialog to open / close
DIALOG_DELAY_S = 1.5
ACCEPT_THRESHOLD = 0.9


def find_truck(game):
  """The truck button's Point when a delivery is available (black
  truck, no counter / countdown), else None."""
  truck = game.screen.find_exact(
    'food_delivery_available', game.coords.food_delivery_roi)
  if truck is None:
    return None
  return Point(game.coords.side_button_tap_x, truck.center.y)


def accept(game, truck):
  """Open Food Delivery and accept the first order.

  The dialog closes by itself after Accept. Returns True when the
  order was accepted.
  """
  game.device.tap(truck)
  time.sleep(DIALOG_DELAY_S)
  game.screen.capture()
  if not _is_accept_shown(game):
    log.info('Food Delivery dialog not found')
    popups.close_popup(game)
    return False
  game.device.tap(game.coords.food_delivery_accept)
  time.sleep(DIALOG_DELAY_S)
  game.screen.capture()
  if _is_accept_shown(game):
    log.info('Food Delivery dialog still open after Accept')
    popups.close_popup(game)
    return False
  log.info('Food Delivery accepted (first order)')
  return True


def _is_accept_shown(game):
  """Accept button of the first order in the dialog."""
  return game.screen.has('food_delivery_accept',
                         game.coords.food_delivery_accept_roi,
                         ACCEPT_THRESHOLD)
