"""ScaledCoords: coords/reference.py scaled to the phone's resolution."""

from coords import reference
from coords.geometry import Point, Region, Swipe


class ScaledCoords:
  """Screen positions of coords/reference.py on this phone.

    sc = ScaledCoords(1080, 2400)
    sc.upgrade_button          # Point, scaled
    sc.station_tap_offset_y    # number ending in _y, scaled by y
  """

  def __init__(self, width, height):
    self.x_scale = width / reference.REFERENCE_WIDTH
    self.y_scale = height / reference.REFERENCE_HEIGHT
    self.screen_width = width

  def __getattr__(self, name):
    # Called only for names that are not set in __init__
    try:
      value = getattr(reference, name)
    except AttributeError:
      raise AttributeError(
        f'{name!r} is not defined in coords/reference.py') from None
    return self._scale(name, value)

  def _scale(self, name, value):
    if isinstance(value, Point):
      return Point(self._x(value.x), self._y(value.y))
    if isinstance(value, Region):
      return Region(self._x(value.left), self._y(value.top),
                    self._x(value.right), self._y(value.bottom))
    if isinstance(value, Swipe):
      return Swipe(self._scale(name, value.start),
                   self._scale(name, value.end))
    if isinstance(value, tuple):
      return tuple(self._scale(name, item) for item in value)
    return self._scale_number(name, value)

  def _scale_number(self, name, value):
    if name.endswith('_x'):
      return self._x(value)
    if name.endswith('_y'):
      return self._y(value)
    return value

  def _x(self, value):
    return round(value * self.x_scale)

  def _y(self, value):
    return round(value * self.y_scale)
