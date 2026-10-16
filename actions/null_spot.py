"""Null spot: an empty spot on the restaurant tapped to close station
popups, placed just below the top bar."""

import logging

from actions import start_dialogs
from bot.logger import key_log
from coords.geometry import Point
from vision.top_bar import find_top_bar_line

log = logging.getLogger(__name__)


def place_below_top_bar(game):
  """Place the null spot just below the top bar's black line.

  Called once at start. The status bar height differs between phones,
  so the spot can't be derived from the resolution. If the line is not
  found, the fallback from coords/reference.py stays and an ERROR is
  logged.
  """
  # On a dimmed screen the line comes out wrong
  if not start_dialogs.close_dimming_dialogs(game):
    _log_fallback(game, 'screen stays dimmed by a dialog')
    return
  line_y = find_top_bar_line(
    game.screen.bgr, game.coords.top_bar_line_min_rows_y)
  if line_y is None:
    _log_fallback(game, 'no black line in the top band')
    return
  game.null_spot = Point(
    game.null_spot.x, line_y + game.coords.null_spot_below_top_bar_y)
  log.info('Null spot below the top bar (y=%d): (%d, %d)',
           line_y, *game.null_spot)


def _log_fallback(game, reason):
  log.error(
    'Top bar not found (%s), the null spot stays at the fallback '
    '(%d, %d) from coords/reference.py. Risky: if the top bar covers '
    'it, station popups stay open; if it is too low, it can hit a '
    'customer bubble, open the Investor dialog and start an ad. Fix: '
    'check a screenshot of this phone and adjust actions/null_spot.py.',
    reason, *game.null_spot)
  key_log.error(
    'ERROR - Top bar not found (%s), null spot at fallback (%d, %d), '
    'popups may stay open or an ad may start; fix actions/null_spot.py',
    reason, *game.null_spot)
