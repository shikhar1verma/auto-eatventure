"""Game: what every game action works with."""


class Game:
  """The phone, its last screenshot and the screen positions."""

  def __init__(self, device, screen, coords):
    """device: android.Device, screen: vision.Screen, coords:
    coords.ScaledCoords."""
    self.device = device
    self.screen = screen
    self.coords = coords
    # Tapped to close station popups; moved below the top bar at start
    # (actions/null_spot.py)
    self.null_spot = coords.null_spot_fallback
