"""
scaled_coords.py - Resolution-aware coordinate wrapper

Usage:
    from scaled_coords import ScaledCoords, detect_resolution

    width, height = detect_resolution(device)
    sc = ScaledCoords(width, height)

    # Access any coordinate from coords.py — _x attrs scale by x_scale,
    # _y attrs scale by y_scale, everything else passes through unscaled.
    x = sc.settings_x    # scaled
    y = sc.settings_y    # scaled
    eps = sc.dbscan_eps  # unscaled (not a pixel position)
"""

import re
import coords

from logger import get_logger

log = get_logger(__name__)


def detect_resolution(device) -> tuple[int, int]:
    """Query actual screen resolution from the device via ADB.

    Returns:
        (width, height) as integers
    """
    output = device.shell("wm size")
    # Output is like "Physical size: 1220x2712" or "Override size: 1080x2400"
    match = re.search(r"(\d+)x(\d+)", output)
    if not match:
        raise RuntimeError(f"Could not parse resolution from 'wm size' output: {output!r}")
    width, height = int(match.group(1)), int(match.group(2))
    log.info("Detected resolution: %dx%d (reference: %dx%d)",
             width, height,
             coords.REFERENCE_WIDTH, coords.REFERENCE_HEIGHT)
    return width, height


def detect_resolution_appium(driver) -> tuple[int, int]:
    """Query actual screen resolution from an Appium WebDriver instance.

    Returns:
        (width, height) as integers
    """
    size = driver.get_window_size()
    width, height = size['width'], size['height']
    log.info("Detected resolution (Appium): %dx%d "
             "(reference: %dx%d)",
             width, height,
             coords.REFERENCE_WIDTH, coords.REFERENCE_HEIGHT)
    return width, height


class ScaledCoords:
    """Proxy to coords module that auto-scales coordinate values to the actual device resolution.

    Attributes ending in '_x' are scaled by the horizontal scale factor.
    Attributes ending in '_y' are scaled by the vertical scale factor.
    All other attributes pass through unscaled.
    """

    def __init__(self, actual_width: int, actual_height: int):
        # Store scale factors in __dict__ directly to avoid triggering __getattr__
        object.__setattr__(self, '_x_scale', actual_width / coords.REFERENCE_WIDTH)
        object.__setattr__(self, '_y_scale', actual_height / coords.REFERENCE_HEIGHT)

    @property
    def x_scale(self) -> float:
        return object.__getattribute__(self, '_x_scale')

    @property
    def y_scale(self) -> float:
        return object.__getattribute__(self, '_y_scale')

    @property
    def screen_width(self) -> int:
        return round(coords.REFERENCE_WIDTH * self.x_scale)

    @property
    def screen_height(self) -> int:
        return round(coords.REFERENCE_HEIGHT * self.y_scale)

    def __getattr__(self, name: str):
        try:
            val = getattr(coords, name)
        except AttributeError:
            raise AttributeError(f"'ScaledCoords' has no attribute {name!r} (not found in coords module)")

        if isinstance(val, int) or isinstance(val, float):
            x_scale = object.__getattribute__(self, '_x_scale')
            y_scale = object.__getattribute__(self, '_y_scale')
            if name.endswith('_x'):
                return round(val * x_scale)
            elif name.endswith('_y'):
                return round(val * y_scale)

        return val
