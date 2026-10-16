"""Timer: when an occasional action is due again."""

import time


class Timer:
  """Due right away, then again after the time set by postpone()."""

  def __init__(self):
    self._due = 0

  def is_due(self):
    return time.monotonic() >= self._due

  def postpone(self, seconds):
    """Not due for the next seconds."""
    self._due = time.monotonic() + seconds

  def reset(self):
    """Due right away."""
    self._due = 0
