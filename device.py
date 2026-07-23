"""
device.py - ADB device interaction layer

Handles all communication with the Android device:
screenshot capture, tap/swipe/text input, and app lifecycle.
"""

import io
import os
import subprocess
import sys
import time

import cv2
import numpy as np
from adbutils import adb
from PIL import Image

from logger import get_logger
from scaled_coords import ScaledCoords, detect_resolution

log = get_logger(__name__)


class Device:
  """ADB device wrapper for input and screenshot operations."""

  def __init__(self):
    serial = os.getenv("device_serial", "").strip()
    if serial:
      self.device = adb.device(serial=serial)
    else:
      devices = adb.device_list()
      if not devices:
        raise RuntimeError(
          "No ADB devices connected. "
          "Connect your phone and enable USB Debugging.")
      self.device = devices[0]
      log.warning("No device_serial in .env — "
                  "using first connected device: %s",
                  self.device.serial)

    actual_w, actual_h = detect_resolution(self.device)
    self.sc = ScaledCoords(actual_w, actual_h)
    self.package_name = "com.hwqgrhhjfd.idlefastfood"

    # Current frame in multiple color spaces (refreshed each capture)
    self.current_cv2_sc = None
    self.current_cv2_sc_grayscale = None
    self.current_cv2_sc_bgr2hsv = None

  def capture_screenshot(self):
    """Capture screenshot in memory via ADB."""
    if sys.platform == 'win32':
      adb_command = f'adb -s {self.device.serial} shell screencap -p'
      output = subprocess.check_output(adb_command.split())
      output = output.replace(b'\r\n', b'\n')
    else:
      adb_command = \
        f'adb -s {self.device.serial} exec-out screencap -p'
      output = subprocess.check_output(adb_command.split())

    pilimg = Image.open(io.BytesIO(output))
    pilimg.load()
    pilimg = pilimg.convert("RGB")

    open_cv_image = np.array(pilimg)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    self.current_cv2_sc = open_cv_image
    self.current_cv2_sc_grayscale = cv2.cvtColor(
      open_cv_image, cv2.COLOR_BGR2GRAY)
    self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
      open_cv_image, cv2.COLOR_BGR2HSV)

  def capture_screenshot_on_disk(self, path):
    """Capture screenshot and save to disk."""
    pilimg = self.device.screenshot()
    pilimg.save(path)
    self.current_cv2_sc = cv2.imread(path)
    self.current_cv2_sc_grayscale = cv2.imread(
      path, cv2.IMREAD_GRAYSCALE)
    self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
      self.current_cv2_sc, cv2.COLOR_BGR2HSV)

  def click(self, coords):
    """Tap at coordinates. Accepts dict {x,y} or list [x,y]."""
    if type(coords) is dict:
      self.device.shell(
        f"input tap {coords['x']} {coords['y']}")
    if type(coords) is list:
      self.device.shell(
        f"input tap {coords[0]} {coords[1]}")

  def click_and_hold(self, x, y, hold_duration=1000):
    """Long press via zero-distance swipe."""
    self.device.shell(
      f'input swipe {x} {y} {x} {y} {hold_duration}')

  def input_text(self, text):
    """Type text via ADB input."""
    escaped_text = text.replace(" ", "%s").replace(
      "&", "\\&").replace("|", "\\|")
    self.device.shell(f"input text '{escaped_text}'")

  def swipe(self, start, end):
    """Swipe from start to end coordinates."""
    self.device.swipe(
      start['x'], start['y'], end['x'], end['y'])

  def start_app(self):
    """Launch the game app."""
    self.device.shell(
      f"monkey -p {self.package_name} "
      f"-c android.intent.category.LAUNCHER 1")

  def close_app(self):
    """Force-stop the game app."""
    self.device.shell(f"am force-stop {self.package_name}")
