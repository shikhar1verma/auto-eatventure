"""Station upgrade icons found by shape and color (they pulse, so
template matching would miss them)."""

import cv2
import numpy as np

from coords.geometry import Point

# Station upgrade icon: red circle (HSV (1, 179, 255)) with a white up
# arrow. The arrow is found as a white shape, then the red circle
# around it is checked. Under a dialog the red is dark (V ~120), so
# icons on a dimmed screen are not found. "Double"/"Instant" labels
# tint the arrow pink, hence the loose white.
ARROW_WHITE = ((0, 0, 225), (180, 70, 255))
CIRCLE_RED = ((0, 150, 235), (3, 210, 255))
# Arrow shape (bounding box): aspect, filled share, empty top corners
# (an X has them full), filled bottom middle (the stem) and center
# (a letter "o" has it empty)
ARROW_ASPECT = (0.7, 1.3)
ARROW_FILL = (0.4, 0.75)
ARROW_MAX_TOP_CORNERS = 0.3
ARROW_MIN_STEM = 0.3
ARROW_MIN_CENTER = 0.5
# The circle is sampled on its upper half (labels below the icon and
# the side panel cover parts of it), at this multiple of the arrow
# height from the arrow's center; at least this many of the 9 points
# must be icon red
CIRCLE_RADIUS = 0.8
CIRCLE_MIN_HITS = 4
CIRCLE_POINTS = [(np.cos(a), -np.sin(a)) for a in np.linspace(0, np.pi, 9)]


def find_upgrade_icons(image_hsv, min_height, max_height):
  """Centers (Points) of the arrows of all station upgrade icons.

  The arrow height range is in screen pixels (the icons pulse).
  """
  white = cv2.inRange(image_hsv, *map(np.array, ARROW_WHITE))
  red = cv2.inRange(image_hsv, *map(np.array, CIRCLE_RED))
  _, labels, stats, _ = cv2.connectedComponentsWithStats(
    white, connectivity=4)
  icons = []
  # Component 0 is the background
  for i in range(1, len(stats)):
    x, y, w, h, area = stats[i]
    if not min_height <= h <= max_height:
      continue
    if not _is_arrow(labels[y:y + h, x:x + w] == i, area):
      continue
    center = Point(int(x + w // 2), int(y + h // 2))
    if _is_circle_around(red, center, h):
      icons.append(center)
  return icons


def _is_arrow(shape, area):
  """Check the shape (bool mask of its bounding box) of a white
  component."""
  h, w = shape.shape
  if not ARROW_ASPECT[0] <= w / h <= ARROW_ASPECT[1]:
    return False
  if not ARROW_FILL[0] <= area / (w * h) <= ARROW_FILL[1]:
    return False
  band = max(1, h // 5)
  third = max(1, w // 3)
  top_corners = np.concatenate(
    [shape[:band, :third], shape[:band, w - third:]], axis=1)
  stem = shape[h - band:, third:w - third]
  center = shape[h // 2 - 1:h // 2 + 2, w // 2 - 1:w // 2 + 2]
  return (top_corners.mean() <= ARROW_MAX_TOP_CORNERS
          and stem.mean() >= ARROW_MIN_STEM
          and center.mean() >= ARROW_MIN_CENTER)


def _is_circle_around(red, center, arrow_height):
  """Check the red circle (mask) around an arrow."""
  height, width = red.shape
  radius = CIRCLE_RADIUS * arrow_height
  hits = 0
  for dx, dy in CIRCLE_POINTS:
    x = int(center.x + dx * radius)
    y = int(center.y + dy * radius)
    if 0 <= x < width and 0 <= y < height and red[y, x]:
      hits += 1
  return hits >= CIRCLE_MIN_HITS
