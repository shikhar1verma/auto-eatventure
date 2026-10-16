"""Reward of the "Restaurant Race ended!" dialog."""

import logging
import time

from auto_eatventure.logger import key_log
from auto_eatventure.coords.geometry import Region

log = logging.getLogger(__name__)

# Title / Claim templates score 0.96-1.00, <= 0.57 on all other screens
TEMPLATE_THRESHOLD = 0.8
CLAIM_DELAY_S = 1.5
# The templates match a dimmed dialog too; Claim is tapped only when
# its button is bright (mean V ~240), i.e. no other dialog covers it
CLAIM_MIN_BRIGHTNESS = 200


def claim(game):
  """Claim the reward of the "Restaurant Race ended!" dialog.

  The dialog has no X, only Claim (gems, no ad), and blocks the game.
  Claim is searched only below the dialog's title, so it can't be
  another dialog's Claim (the Investor's starts an ad). Returns True
  when Claim was tapped.
  """
  screen = game.screen
  title = screen.find('race_ended_title', threshold=TEMPLATE_THRESHOLD)
  if title is None:
    return False
  below_title = Region(0, title.bottom,
                       screen.region.right, screen.region.bottom)
  button = screen.find('race_claim', below_title, TEMPLATE_THRESHOLD)
  if button is None:
    log.warning('Restaurant Race ended, but its Claim not found')
    return False
  if button.crop(screen.hsv)[:, :, 2].mean() < CLAIM_MIN_BRIGHTNESS:
    log.info('Restaurant Race ended dialog is covered, not claiming')
    return False
  log.info('Restaurant Race ended - claiming the reward at (%d, %d)',
           *button.center)
  key_log.info('RACE - Restaurant Race reward claimed')
  game.device.tap(button.center)
  time.sleep(CLAIM_DELAY_S)
  screen.capture()
  return True
