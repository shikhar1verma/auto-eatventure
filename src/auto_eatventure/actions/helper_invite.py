"""Invite a helper: inviting the first helper whenever possible."""

import logging
import time

from auto_eatventure.actions import popups

log = logging.getLogger(__name__)

# Pause after an invite, like for Food Delivery. A helper works ~4 min
# and the cooldown is ~30 min, so it never delays a real invite. A
# failed attempt costs up to ~15 s (the list may not load at all, e.g.
# offline), so it is retried much later.
PAUSE_S = 60
RETRY_S = 10 * 60

# The dialog shows "Loading..." for a few seconds before the helper
# list appears; it is awaited up to this long
DIALOG_TIMEOUT_S = 10
# Time for the dialog to close after Invite
DIALOG_DELAY_S = 1.5
# Max difference of the "available" helper button. Lower than the
# default: the black person with only an ad icon under it scores ~0.03.
AVAILABLE_MAX_DIFFERENCE = 0.015
INVITE_THRESHOLD = 0.8


def is_available(game):
  """The helper button shows a black person with nothing under it (no
  green work countdown, no ad offer, not grey cooldown)."""
  return game.screen.find_exact(
    'helper_available', game.coords.helper_roi,
    AVAILABLE_MAX_DIFFERENCE) is not None


def invite(game):
  """Open "Invite a helper" and invite the first helper.

  The helper works for ~4 min, then the button offers an ad (never
  tapped) and a ~30 min cooldown follows. The dialog closes by itself
  after Invite. Returns True when the helper was invited.
  """
  # Confirm on a fresh screenshot, so a frame caught between two
  # states (e.g. countdown -> ad offer) doesn't tap the ad offer
  time.sleep(1)
  game.screen.capture()
  if not is_available(game):
    log.info('Helper button no longer available')
    return False
  game.device.tap(game.coords.helper_button)
  if not _wait_for_invite_button(game):
    log.info('Invite a helper dialog not found')
    popups.close_popup(game)
    return False
  game.device.tap(game.coords.helper_invite)
  time.sleep(DIALOG_DELAY_S)
  game.screen.capture()
  if _is_invite_shown(game):
    log.info('Invite a helper dialog still open after Invite')
    popups.close_popup(game)
    return False
  log.info('Helper invited (first helper)')
  return True


def _wait_for_invite_button(game):
  deadline = time.monotonic() + DIALOG_TIMEOUT_S
  while time.monotonic() < deadline:
    time.sleep(1)
    game.screen.capture()
    if _is_invite_shown(game):
      return True
  return False


def _is_invite_shown(game):
  """Invite button of the first helper in the dialog."""
  return game.screen.has('helper_invite', game.coords.helper_invite_roi,
                         INVITE_THRESHOLD)
