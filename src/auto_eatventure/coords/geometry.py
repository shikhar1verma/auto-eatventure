"""Point, Region and Swipe: the shapes screen positions are made of."""

from typing import NamedTuple


class Point(NamedTuple):
  """A pixel on the screen."""
  x: int
  y: int


class Region(NamedTuple):
  """A rectangle on the screen (right and bottom excluded)."""
  left: int
  top: int
  right: int
  bottom: int

  @classmethod
  def around(cls, center, half_width, half_height):
    """Region of the given half sizes centered on a Point."""
    return cls(center.x - half_width, center.y - half_height,
               center.x + half_width, center.y + half_height)

  @property
  def center(self):
    return Point((self.left + self.right) // 2,
                 (self.top + self.bottom) // 2)

  def crop(self, image):
    """The part of an image (numpy array) inside this region."""
    return image[self.top:self.bottom, self.left:self.right]

  def moved(self, dx, dy):
    """The same region moved by (dx, dy)."""
    return Region(self.left + dx, self.top + dy,
                  self.right + dx, self.bottom + dy)


class Swipe(NamedTuple):
  """A swipe gesture from start to end."""
  start: Point
  end: Point
