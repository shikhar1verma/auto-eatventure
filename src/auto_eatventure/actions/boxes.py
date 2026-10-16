"""Food boxes dropped on the restaurant."""

import logging
import time

log = logging.getLogger(__name__)

BOX_THRESHOLD = 0.7


def open_all(game):
  """Tap all visible boxes.

  There are two box looks; the second is searched only when the first
  is not found.
  """
  boxes = (game.screen.find_all('box', BOX_THRESHOLD)
           or game.screen.find_all('box2', BOX_THRESHOLD))
  for box in boxes:
    log.info('Opening box')
    game.device.tap(box)
    time.sleep(0.2)
