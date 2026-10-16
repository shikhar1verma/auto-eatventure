"""
template_matcher.py - OpenCV template matching engine

Handles template loading, resizing, matching strategies
(HSV, grayscale, color-masked, raw BGR), and DBSCAN clustering.
"""

import os

import cv2
import numpy as np
from sklearn.cluster import DBSCAN

from logger import get_logger

log = get_logger(__name__)

# Station upgrade icon: red circle (HSV (1, 179, 255)) with a white up
# arrow. The arrow is found as a white shape, then the red circle
# around it is checked. Under a dialog the red is dark (V ~120), so
# icons on a dimmed screen are not found. "Double"/"Instant" labels
# tint the arrow pink, hence the loose white.
UPGRADE_ARROW_WHITE = ((0, 0, 225), (180, 70, 255))
UPGRADE_CIRCLE_RED = ((0, 150, 235), (3, 210, 255))
# Arrow shape (bounding box): aspect, filled share, empty top corners
# (an X has them full), filled bottom middle (the stem) and center
# (a letter "o" has it empty)
UPGRADE_ARROW_ASPECT = (0.7, 1.3)
UPGRADE_ARROW_FILL = (0.4, 0.75)
UPGRADE_ARROW_MAX_TOP_CORNERS = 0.3
UPGRADE_ARROW_MIN_STEM = 0.3
UPGRADE_ARROW_MIN_CENTER = 0.5
# The circle is sampled on its upper half (labels below the icon and
# the side panel cover parts of it), at this multiple of the arrow
# height from the arrow's center; at least this many of the 9 points
# must be icon red
UPGRADE_CIRCLE_RADIUS = 0.8
UPGRADE_CIRCLE_MIN_HITS = 4
UPGRADE_CIRCLE_POINTS = [
  (np.cos(a), -np.sin(a)) for a in np.linspace(0, np.pi, 9)]


class TemplateMatcher:
  """Loads and matches templates against screenshots."""

  def __init__(self, sc):
    self.sc = sc
    self.template_x_scale = sc.x_scale
    self.template_y_scale = sc.y_scale

    scale_override = os.getenv(
      "TEMPLATE_SCALE_OVERRIDE", "").strip()
    if scale_override:
      try:
        override = float(scale_override)
        self.template_x_scale = override
        self.template_y_scale = override
        log.info(
          "TEMPLATE_SCALE_OVERRIDE=%.4f — overriding "
          "auto-scale (was x=%.4f, y=%.4f)",
          override, sc.x_scale, sc.y_scale)
      except ValueError:
        log.warning(
          "Invalid TEMPLATE_SCALE_OVERRIDE=%r — "
          "ignored, using resolution-based scale "
          "x=%.4f, y=%.4f",
          scale_override, sc.x_scale, sc.y_scale)
    else:
      log.info(
        "Template scale: x=%.4f, y=%.4f",
        self.template_x_scale, self.template_y_scale)

    self.debug = os.getenv(
      "DEBUG_TEMPLATE_MATCHING", "0").strip() == "1"

    self.matching_screenshots_path = {
      'notification':
        './matching_screenshots/notification.png',
      'first_lemondae_stand_open':
        './matching_screenshots/first_lemonade_stand_open.png',
      'open_button':
        './matching_screenshots/open_button.png',
      'welcome_city_okay':
        './matching_screenshots/welcome_city_okay.png',
      'settings':
        './matching_screenshots/settings.png',
      'offline_earnings':
        './matching_screenshots/offline_earnings.png',
      'single_upgrade':
        './matching_screenshots/single_upgrade.png',
      'box':
        './matching_screenshots/box.png',
      'box2':
        './matching_screenshots/box2.png',
      'race_ended_title':
        './matching_screenshots/race_ended_title.png',
      'race_claim':
        './matching_screenshots/race_claim.png',
      'buy_better_food_button':
        './matching_screenshots/buy_better_food_button.png',
      'go_next_level':
        './matching_screenshots/go_next_level_icon.png',
      'no_boost_indicator_2x':
        './matching_screenshots/no_boost_indicator_2x.png',
      'fly_next_city_icon':
        './matching_screenshots/fly_next_city_icon.png',
      'small_investor_icon':
        './matching_screenshots/small_investor_icon.png',
      'investor':
        './matching_screenshots/investor.png',
      'chest_icon':
        './matching_screenshots/chest_icon.png',
      'popup_close_cross':
        './matching_screenshots/popup_close_cross.png',
      'popular_dish_select':
        './matching_screenshots/popular_dish_select.png',
      'popular_dish_start':
        './matching_screenshots/popular_dish_start.png',
      'popular_dish_stop':
        './matching_screenshots/popular_dish_stop.png',
      'food_delivery_available':
        './matching_screenshots/food_delivery_available.png',
      'food_delivery_accept':
        './matching_screenshots/food_delivery_accept.png',
      'helper_available':
        './matching_screenshots/helper_available.png',
      'helper_invite':
        './matching_screenshots/helper_invite.png',
      'adventure_zeus_key':
        './matching_screenshots/adventure_zeus_key.png',
      'adventure_pirates_key':
        './matching_screenshots/adventure_pirates_key.png',
      'adventure_zeus_dialog_key':
        './matching_screenshots/adventure_zeus_dialog_key.png',
      'adventure_pirates_dialog_key':
        './matching_screenshots/adventure_pirates_dialog_key.png',
      'ads_crosses': {
        'cross1':
          './matching_screenshots/ads_crosses/cross1.png',
      }
    }
    self.templates = {}
    self._load_all_templates()

  # ── Template loading ──────────────────────────────────────

  def _resize_template(self, template):
    h, w = template.shape[:2]
    target_w = max(1, round(w * self.template_x_scale))
    target_h = max(1, round(h * self.template_y_scale))
    if target_w == w and target_h == h:
      return template
    interpolation = (cv2.INTER_AREA
                     if target_w < w or target_h < h
                     else cv2.INTER_LINEAR)
    return cv2.resize(
      template, (target_w, target_h),
      interpolation=interpolation)

  def _load_template(self, path):
    simple = cv2.imread(path)
    if simple is None:
      raise FileNotFoundError(
        f"Template not found or unreadable: {path}")
    simple = self._resize_template(simple)
    return {
      'simple': simple,
      'grayscale': cv2.cvtColor(simple, cv2.COLOR_BGR2GRAY),
      'bgr2hsv': cv2.cvtColor(simple, cv2.COLOR_BGR2HSV),
    }

  def _load_all_templates(self):
    for key, value in self.matching_screenshots_path.items():
      if key == 'ads_crosses':
        self.templates[key] = {}
        for k, v in value.items():
          self.templates[key][k] = self._load_template(v)
      else:
        self.templates[key] = self._load_template(value)

  # ── Core matching ─────────────────────────────────────────

  def find_template(self, image, template, threshold=0.8):
    """Find single best match. Returns (x, y) or None."""
    result = cv2.matchTemplate(
      image, template, cv2.TM_CCOEFF_NORMED)
    matches = cv2.minMaxLoc(result)
    if self.debug:
      log.debug("matchTemplate result: %s", matches)
    _, max_val, _, max_loc = matches
    if max_val > threshold:
      return max_loc
    return None

  def find_all_templates(self, image, template,
                         end=False, threshold=0.8):
    """Find all matches above threshold, clustered by DBSCAN.

    Returns list of [x, y] centroids.
    """
    if len(template.shape[::-1]) == 2:
      template_width, template_height = template.shape[::-1]
    else:
      template_width, template_height = \
        template.shape[::-1][1:]

    result = cv2.matchTemplate(
      image, template, cv2.TM_CCOEFF_NORMED)
    if self.debug:
      log.debug("matchTemplate minMaxLoc: %s",
                cv2.minMaxLoc(result))
    locations = np.where(result >= threshold)

    coordinates = []
    for pt in zip(*locations[::-1]):
      if end:
        x_center = pt[0] + template_width
        y_center = pt[1] + template_height
      else:
        x_center = pt[0] + template_width // 2
        y_center = pt[1] + template_height // 2
      coordinates.append((x_center, y_center))

    coord_array = np.array(coordinates)
    if len(coord_array) == 0:
      return []

    dbscan = DBSCAN(eps=self.sc.dbscan_eps, min_samples=5)
    dbscan.fit(coord_array)

    centroids = []
    for cluster_label in set(dbscan.labels_):
      if cluster_label != -1:
        cluster_coords = \
          coord_array[dbscan.labels_ == cluster_label]
        centroid = np.mean(cluster_coords, axis=0)
        centroids.append(centroid)

    return [c.astype(int).tolist() for c in centroids]

  # ── Matching strategies ───────────────────────────────────

  def match_hsv(self, screenshot_hsv, template_key,
                threshold=0.8):
    """Match using HSV color space. Returns (x,y) or None."""
    hsv_template = self.templates[template_key]['bgr2hsv']
    return self.find_template(
      screenshot_hsv, hsv_template, threshold)

  def match_grayscale(self, screenshot_gray, template_key,
                      threshold=0.8):
    """Match using grayscale. Returns (x,y) or None."""
    template = self.templates[template_key]['grayscale']
    return self.find_template(
      screenshot_gray, template, threshold)

  def match_bgr_sqdiff(self, screenshot_bgr, template_key,
                       max_diff=0.02):
    """Match raw BGR by squared difference. Returns (x,y) or None.

    Unlike TM_CCOEFF_NORMED it is sensitive to brightness, so it
    can tell a black icon from the same icon greyed out.
    Lower diff = better match (0 = identical).
    """
    template = self.templates[template_key]['simple']
    result = cv2.matchTemplate(
      screenshot_bgr, template, cv2.TM_SQDIFF_NORMED)
    min_val, _, min_loc, _ = cv2.minMaxLoc(result)
    if self.debug:
      log.debug("sqdiff %s: %.4f", template_key, min_val)
    if min_val < max_diff:
      return min_loc
    return None

  def is_hsv_match(self, screenshot_hsv, template_key,
                   threshold=0.8):
    """Check if template matches in HSV. Returns bool."""
    return self.match_hsv(
      screenshot_hsv, template_key, threshold) is not None

  def is_grayscale_match(self, screenshot_gray, template_key,
                         threshold=0.8):
    """Check if template matches in grayscale. Returns bool."""
    return self.match_grayscale(
      screenshot_gray, template_key, threshold) is not None

  # ── Station upgrade icons ─────────────────────────────────

  def find_upgrade_icons(self, image_hsv, min_height, max_height):
    """Find station upgrade icons (red circle, white up arrow).

    The arrow height range is in screen pixels (the icons pulse).
    Returns a list of [x, y] arrow centers.
    """
    white = cv2.inRange(image_hsv, *map(np.array, UPGRADE_ARROW_WHITE))
    red = cv2.inRange(image_hsv, *map(np.array, UPGRADE_CIRCLE_RED))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
      white, connectivity=4)
    icons = []
    for i in range(1, count):
      x, y, w, h, area = stats[i]
      if not min_height <= h <= max_height:
        continue
      if not self._is_upgrade_arrow(
          labels[y:y + h, x:x + w] == i, area):
        continue
      cx = x + w // 2
      cy = y + h // 2
      if self._is_upgrade_circle(red, cx, cy, h):
        icons.append([int(cx), int(cy)])
    return icons

  @staticmethod
  def _is_upgrade_arrow(shape, area):
    """Check the shape (bool mask of its bounding box) of a white
    component."""
    h, w = shape.shape
    if not UPGRADE_ARROW_ASPECT[0] <= w / h <= UPGRADE_ARROW_ASPECT[1]:
      return False
    if not UPGRADE_ARROW_FILL[0] <= area / (w * h) \
        <= UPGRADE_ARROW_FILL[1]:
      return False
    band = max(1, h // 5)
    third = max(1, w // 3)
    top_corners = np.concatenate(
      [shape[:band, :third], shape[:band, w - third:]], axis=1)
    stem = shape[h - band:, third:w - third]
    center = shape[h // 2 - 1:h // 2 + 2, w // 2 - 1:w // 2 + 2]
    return (top_corners.mean() <= UPGRADE_ARROW_MAX_TOP_CORNERS
            and stem.mean() >= UPGRADE_ARROW_MIN_STEM
            and center.mean() >= UPGRADE_ARROW_MIN_CENTER)

  @staticmethod
  def _is_upgrade_circle(red, cx, cy, arrow_height):
    """Check the red circle around an arrow centered at (cx, cy)."""
    height, width = red.shape
    radius = UPGRADE_CIRCLE_RADIUS * arrow_height
    hits = 0
    for dx, dy in UPGRADE_CIRCLE_POINTS:
      px = int(cx + dx * radius)
      py = int(cy + dy * radius)
      if 0 <= px < width and 0 <= py < height and red[py, px]:
        hits += 1
    return hits >= UPGRADE_CIRCLE_MIN_HITS

  # ── Color masking ─────────────────────────────────────────

  def apply_investor_mask(self, image, tolerance=15):
    """Isolate investor-specific HSV colors."""
    colors = [
      (26, 80, 105), (25, 94, 119),
      (26, 108, 139), (26, 110, 135)]
    return self._apply_color_mask(image, colors, tolerance)

  def apply_box_mask(self, image, tolerance=8):
    """Isolate box-specific HSV colors."""
    colors = [
      (22, 116, 255), (13, 152, 171),
      (14, 155, 140), (19, 130, 232),
      (19, 126, 254), (18, 130, 239)]
    return self._apply_color_mask(image, colors, tolerance)

  def _apply_color_mask(self, image, colors, tolerance):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    combined_mask = np.zeros_like(hsv_image[:, :, 0])
    for color in colors:
      lower = np.array([
        max(color[0] - tolerance, 0),
        max(color[1] - tolerance, 0),
        max(color[2] - tolerance, 0)])
      upper = np.array([
        min(color[0] + tolerance, 180),
        min(color[1] + tolerance, 255),
        min(color[2] + tolerance, 255)])
      mask = cv2.inRange(hsv_image, lower, upper)
      combined_mask = cv2.bitwise_or(combined_mask, mask)
    return cv2.bitwise_and(image, image, mask=combined_mask)

  def color_ratio(self, image_hsv, ranges):
    """Fraction of pixels inside any of the (lower, upper) HSV
    ranges."""
    mask = np.zeros(image_hsv.shape[:2], np.uint8)
    for lower, upper in ranges:
      mask |= cv2.inRange(image_hsv, np.array(lower), np.array(upper))
    return np.count_nonzero(mask) / mask.size

  # ── Pixel color check ────────────────────────────────────

  def is_pixel_color_between(self, image, start_coords,
                             end_coords, color_to_check):
    """Check if a color exists on a line between two points."""
    x1, y1 = start_coords['x'], start_coords['y']
    x2, y2 = end_coords['x'], end_coords['y']
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    x_inc = dx / steps
    y_inc = dy / steps

    for i in range(steps + 1):
      x = int(x1 + i * x_inc)
      y = int(y1 + i * y_inc)
      pixel_color = image[y, x]
      if all(pixel_color == color_to_check):
        return True
    return False
