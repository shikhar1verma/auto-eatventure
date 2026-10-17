"""Start of the bot: connect to the phone, wait for the game, play."""

import logging

from auto_eatventure.actions import null_spot, start_dialogs
from auto_eatventure.actions.game import Game
from auto_eatventure.android.device import Device
from auto_eatventure import config
from auto_eatventure.game_loop import GameLoop
from auto_eatventure.logger import key_log, setup_logging
from auto_eatventure.coords import reference
from auto_eatventure.coords.scaled import ScaledCoords
from auto_eatventure.vision.screen import Screen
from auto_eatventure.vision.templates import load_templates

log = logging.getLogger(__name__)


def run():
  """Run the bot until it is stopped."""
  setup_logging(config.LOG_LEVEL, config.LOG_FILE_LEVEL,
                config.LOG_MAX_DAYS)
  log.info('START - Bot started')
  game = _connect()
  game.device.start_app()
  start_dialogs.wait_until_ready(game)
  key_log.info('START - Bot started')
  null_spot.place_below_top_bar(game)
  _log_features()
  GameLoop(game).run()


def _connect():
  """Connect to the phone and prepare everything for its resolution."""
  device = Device(config.DEVICE_SERIAL)
  width, height = device.screen_size()
  log.info('Detected resolution: %dx%d (reference: %dx%d)',
           width, height,
           reference.REFERENCE_WIDTH, reference.REFERENCE_HEIGHT)
  coords = ScaledCoords(width, height)
  templates = load_templates(*_template_scale(coords))
  screen = Screen(device, templates, config.DEBUG_TEMPLATE_MATCHING)
  return Game(device, screen, coords)


def _template_scale(coords):
  """(x, y) scale of the templates: the resolution's, unless
  TEMPLATE_SCALE_OVERRIDE is set."""
  override = config.TEMPLATE_SCALE_OVERRIDE
  if not override:
    log.info('Template scale: x=%.4f, y=%.4f',
             coords.x_scale, coords.y_scale)
    return coords.x_scale, coords.y_scale
  try:
    scale = float(override)
  except ValueError:
    log.warning('Invalid TEMPLATE_SCALE_OVERRIDE=%r — ignored, using '
                'resolution-based scale x=%.4f, y=%.4f',
                override, coords.x_scale, coords.y_scale)
    return coords.x_scale, coords.y_scale
  log.info('TEMPLATE_SCALE_OVERRIDE=%.4f — overriding auto-scale '
           '(was x=%.4f, y=%.4f)', scale, coords.x_scale, coords.y_scale)
  return scale, scale


def _log_features():
  features = (
    ('Popular Dish selection', config.POPULAR_DISH_ENABLED),
    ('Food Delivery', config.FOOD_DELIVERY_ENABLED),
    ('Helper invite', config.HELPER_INVITE_ENABLED),
    ('Collect Adventures', config.COLLECT_ADVENTURES_ENABLED),
  )
  for name, enabled in features:
    log.info('%s: %s', name, 'enabled' if enabled else 'disabled')
