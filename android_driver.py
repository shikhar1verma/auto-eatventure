"""
Android Device Driver

Uses ADB (Android Debug Bridge) via adbutils to interact with Android devices.
"""

import io
import subprocess
from typing import Tuple, Optional
from PIL import Image

try:
    from adbutils import adb
    ADB_AVAILABLE = True
except ImportError:
    ADB_AVAILABLE = False

from device_driver import DeviceDriver


class AndroidDriver(DeviceDriver):
    """Android device driver using ADB."""

    def __init__(self, device_serial: Optional[str] = None):
        """
        Initialize Android driver.

        Args:
            device_serial: Optional specific device serial. If None, uses first available device.
        """
        if not ADB_AVAILABLE:
            raise ImportError("adbutils is required for Android support. "
                              "Install with: pip install adbutils")

        self._device = None
        self._device_serial = device_serial
        self._connected = False
        self._screen_size = None

    def connect(self) -> bool:
        """Connect to the Android device via ADB."""
        try:
            if self._device_serial:
                self._device = adb.device(serial=self._device_serial)
            else:
                self._device = adb.device()

            # Test connection by getting device info
            self._device.shell("echo connected")
            self._connected = True

            # Cache screen size
            self._update_screen_size()

            print(f"Connected to Android device: {self._device.serial}")
            return True
        except Exception as e:
            print(f"Failed to connect to Android device: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the device."""
        self._device = None
        self._connected = False
        print("Disconnected from Android device")

    def screenshot(self) -> Image.Image:
        """Capture screenshot from Android device."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Use subprocess for faster screenshot capture
        adb_command = f'adb -s {self._device.serial} shell screencap -p'
        output = subprocess.check_output(adb_command.split())

        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(output))
        pil_image.load()
        pil_image = pil_image.convert("RGB")

        return pil_image

    def tap(self, x: int, y: int) -> None:
        """Tap at coordinates."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._device.shell(f"input tap {x} {y}")

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Swipe to same point creates a long press
        self._device.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """Perform swipe gesture."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._device.swipe(start_x, start_y, end_x, end_y, duration_ms / 1000.0)

    def input_text(self, text: str) -> None:
        """Input text on device."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Escape special characters
        escaped_text = text.replace(" ", "%s").replace(
            "&", "\\&").replace("|", "\\|")
        self._device.shell(f"input text '{escaped_text}'")

    def launch_app(self, app_identifier: str) -> None:
        """Launch app by package name."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._device.shell(
            f"monkey -p {app_identifier} -c android.intent.category.LAUNCHER 1")

    def close_app(self, app_identifier: str) -> None:
        """Force close app by package name."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._device.shell(f"am force-stop {app_identifier}")

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size in pixels."""
        if self._screen_size:
            return self._screen_size
        self._update_screen_size()
        return self._screen_size

    def _update_screen_size(self) -> None:
        """Update cached screen size."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        output = self._device.shell("wm size")
        # Output format: "Physical size: 1440x3120"
        size_str = output.strip().split(": ")[1]
        width, height = map(int, size_str.split("x"))
        self._screen_size = (width, height)

    @property
    def platform(self) -> str:
        return "android"

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def device(self):
        """Return the underlying adbutils device for advanced usage."""
        return self._device
