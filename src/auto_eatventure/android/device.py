"""Device: the phone over ADB (taps, swipes, screenshots, app start)."""

import io
import logging
import re
import subprocess
import sys

import numpy as np
from adbutils import adb
from PIL import Image

log = logging.getLogger(__name__)

GAME_PACKAGE = 'com.hwqgrhhjfd.idlefastfood'


class Device:
  """The Android phone the game runs on."""

  def __init__(self, serial=''):
    """Connect to the phone with this serial, else the first one."""
    if serial:
      self._adb = adb.device(serial=serial)
      return
    devices = adb.device_list()
    if not devices:
      raise RuntimeError(
        'No ADB devices connected. '
        'Connect your phone and enable USB Debugging.')
    self._adb = devices[0]
    log.warning('No device_serial in .env — '
                'using first connected device: %s', self._adb.serial)

  @property
  def serial(self):
    return self._adb.serial

  def screen_size(self):
    """Return (width, height) of the screen in pixels."""
    output = self._adb.shell('wm size')
    # "Physical size: 1220x2712", maybe also "Override size: ..."
    match = re.search(r'(\d+)x(\d+)', output)
    if not match:
      raise RuntimeError(
        f"Could not parse resolution from 'wm size' output: {output!r}")
    return int(match.group(1)), int(match.group(2))

  def screenshot(self):
    """Return the screen as a BGR image (numpy array)."""
    if sys.platform == 'win32':
      # Kept from the original code: older adb versions on Windows
      # turned \n into \r\n (untested with current adb)
      png = subprocess.check_output(
        ['adb', '-s', self.serial, 'shell', 'screencap', '-p'])
      png = png.replace(b'\r\n', b'\n')
    else:
      png = subprocess.check_output(
        ['adb', '-s', self.serial, 'exec-out', 'screencap', '-p'])
    rgb = Image.open(io.BytesIO(png)).convert('RGB')
    return np.array(rgb)[:, :, ::-1].copy()

  def tap(self, point):
    self._adb.shell(f'input tap {point.x} {point.y}')

  def long_press(self, point, duration_ms):
    """Hold a finger on the point (a swipe that doesn't move)."""
    self._adb.shell(f'input swipe {point.x} {point.y} '
                    f'{point.x} {point.y} {duration_ms}')

  def swipe(self, swipe):
    """Swipe along a coords.geometry.Swipe."""
    self._adb.swipe(swipe.start.x, swipe.start.y,
                    swipe.end.x, swipe.end.y)

  def start_app(self):
    """Launch the game, or bring it to the foreground.

    It does not restart a running game (that needs close_app()).
    """
    self._adb.shell(f'monkey -p {GAME_PACKAGE} '
                    '-c android.intent.category.LAUNCHER 1')

  def close_app(self):
    """Force-stop the game."""
    self._adb.shell(f'am force-stop {GAME_PACKAGE}')
