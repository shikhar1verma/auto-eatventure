"""Template matching: where a template image is found in an image."""

import cv2
import numpy as np
from sklearn.cluster import DBSCAN

from auto_eatventure.coords.geometry import Point, Region

# Matches of one object lie close together; they are merged into one
# when at most this many pixels apart (DBSCAN eps, not scaled)
CLUSTER_MAX_DISTANCE = 10
CLUSTER_MIN_MATCHES = 5


def best_match(image, template):
  """Best match by normalized correlation.

  Returns (score, Region); score 1 = identical. Brightness doesn't
  matter, the shape and colors do.
  """
  result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
  _, score, _, location = cv2.minMaxLoc(result)
  return score, _region_at(location, template)


def closest_match(image, template):
  """Closest match by squared difference.

  Returns (difference, Region); difference 0 = identical. Unlike
  best_match() it is sensitive to brightness, so it can tell a black
  icon from the same icon greyed out.
  """
  result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
  difference, _, location, _ = cv2.minMaxLoc(result)
  return difference, _region_at(location, template)


def all_matches(image, template, threshold):
  """Centers (Points) of all objects matching above the threshold.

  A single object matches at many neighboring positions; they are
  clustered by DBSCAN. Fewer than CLUSTER_MIN_MATCHES matches close
  together are dropped as noise.
  """
  height, width = template.shape[:2]
  result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
  ys, xs = np.where(result >= threshold)
  if len(xs) == 0:
    return []
  centers = np.column_stack((xs + width // 2, ys + height // 2))
  labels = DBSCAN(eps=CLUSTER_MAX_DISTANCE,
                  min_samples=CLUSTER_MIN_MATCHES).fit(centers).labels_
  points = []
  for label in sorted(set(labels) - {-1}):
    x, y = centers[labels == label].mean(axis=0).astype(int)
    points.append(Point(int(x), int(y)))
  return points


def _region_at(location, template):
  x, y = location
  height, width = template.shape[:2]
  return Region(x, y, x + width, y + height)
