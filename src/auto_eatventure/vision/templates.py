"""Template images: the catalog, loading and resizing to the phone."""

import os
from typing import NamedTuple

import cv2

TEMPLATES_DIR = 'matching_screenshots'

# File names (without .png) in TEMPLATES_DIR used by the bot
TEMPLATE_NAMES = (
  'adventure_pirates_dialog_key',
  'adventure_pirates_key',
  'adventure_zeus_dialog_key',
  'adventure_zeus_key',
  'box',
  'box2',
  'chest_icon',
  'fly_next_city_icon',
  'food_delivery_accept',
  'food_delivery_available',
  'go_next_level_icon',
  'helper_available',
  'helper_invite',
  'offline_earnings',
  'open_button',
  'popular_dish_select',
  'popular_dish_start',
  'popular_dish_stop',
  'popup_close_cross',
  'race_claim',
  'race_ended_title',
  'settings',
  'welcome_city_okay',
)


class Template(NamedTuple):
  """A template image in the color spaces it is matched in."""
  bgr: object
  hsv: object

  @property
  def height(self):
    return self.bgr.shape[0]

  @property
  def width(self):
    return self.bgr.shape[1]


def load_templates(x_scale, y_scale):
  """Load all templates of TEMPLATE_NAMES, resized by the scales.

  The templates were cut from screenshots at the reference
  resolution. Returns {name: Template}.
  """
  return {
    name: load_template(
      os.path.join(TEMPLATES_DIR, f'{name}.png'), x_scale, y_scale)
    for name in TEMPLATE_NAMES}


def load_template(path, x_scale, y_scale):
  """Load one template image, resized by the scales."""
  bgr = cv2.imread(path)
  if bgr is None:
    raise FileNotFoundError(f'Template not found or unreadable: {path}')
  bgr = _resize(bgr, x_scale, y_scale)
  return Template(bgr, cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV))


def _resize(image, x_scale, y_scale):
  height, width = image.shape[:2]
  target_width = max(1, round(width * x_scale))
  target_height = max(1, round(height * y_scale))
  if (target_width, target_height) == (width, height):
    return image
  shrinks = target_width < width or target_height < height
  interpolation = cv2.INTER_AREA if shrinks else cv2.INTER_LINEAR
  return cv2.resize(image, (target_width, target_height),
                    interpolation=interpolation)
