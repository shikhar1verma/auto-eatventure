"""HSV color ranges of the game and how much of an image they cover."""

import cv2
import numpy as np

# Red of the badges and of the X (close) buttons of dialogs. Red wraps
# around hue 180, hence two ranges.
RED = [((0, 120, 150), (8, 255, 255)),
       ((172, 120, 150), (180, 255, 255))]


def color_ratio(image_hsv, ranges):
  """Share (0-1) of pixels inside any of the (lower, upper) HSV
  ranges."""
  mask = np.zeros(image_hsv.shape[:2], np.uint8)
  for lower, upper in ranges:
    mask |= cv2.inRange(image_hsv, np.array(lower), np.array(upper))
  return np.count_nonzero(mask) / mask.size
