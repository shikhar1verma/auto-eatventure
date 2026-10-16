"""Screen: the last screenshot of the phone and searches on it."""

import logging

import cv2

from auto_eatventure.coords.geometry import Region
from auto_eatventure.vision import colors, matching

log = logging.getLogger(__name__)


class Screen:
  """The last screenshot in the color spaces the detections need.

  Searches take the template name and an optional Region to search in
  (the whole screen by default) and return Regions in screen pixels.
  """

  def __init__(self, device, templates, debug=False):
    """templates: {name: Template}; debug: log every match score."""
    self._device = device
    self._templates = templates
    self._debug = debug
    self.bgr = None
    self.gray = None
    self.hsv = None

  def capture(self):
    """Take a new screenshot of the phone."""
    self.bgr = self._device.screenshot()
    self.gray = cv2.cvtColor(self.bgr, cv2.COLOR_BGR2GRAY)
    self.hsv = cv2.cvtColor(self.bgr, cv2.COLOR_BGR2HSV)

  @property
  def region(self):
    """The whole screen."""
    height, width = self.bgr.shape[:2]
    return Region(0, 0, width, height)

  def find(self, name, region=None, threshold=0.8):
    """Where the template matches (HSV) above the threshold, else
    None."""
    if region is None:
      region = self.region
    image = region.crop(self.hsv)
    template = self._templates[name].hsv
    if not _fits(template, image):
      return None
    score, match = matching.best_match(image, template)
    self._log_score(name, score)
    if score <= threshold:
      return None
    return match.moved(region.left, region.top)

  def has(self, name, region=None, threshold=0.8):
    """Whether the template matches (HSV) above the threshold."""
    return self.find(name, region, threshold) is not None

  def find_exact(self, name, region=None, max_difference=0.02):
    """Where the template matches (BGR) with a difference below
    max_difference, else None.

    Brightness counts, see matching.closest_match().
    """
    if region is None:
      region = self.region
    image = region.crop(self.bgr)
    template = self._templates[name].bgr
    if not _fits(template, image):
      return None
    difference, match = matching.closest_match(image, template)
    self._log_score(name, difference)
    if difference >= max_difference:
      return None
    return match.moved(region.left, region.top)

  def find_all(self, name, threshold=0.8):
    """Centers (Points) of all matches (BGR) above the threshold."""
    return matching.all_matches(
      self.bgr, self._templates[name].bgr, threshold)

  def color_ratio(self, region, ranges):
    """Share (0-1) of the region's pixels in the HSV ranges."""
    return colors.color_ratio(region.crop(self.hsv), ranges)

  def _log_score(self, name, score):
    if self._debug:
      log.debug('Template %s: score %.4f', name, score)


def _fits(template, image):
  """Whether the template is not larger than the image."""
  return (template.shape[0] <= image.shape[0]
          and template.shape[1] <= image.shape[1])
