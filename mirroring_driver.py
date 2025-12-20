"""
iPhone Mirroring Device Driver

Uses pyautogui to automate iOS apps via iPhone Mirroring on macOS Sequoia (15.0+).
This is MUCH faster than Appium (~0.01s per tap vs ~4s per tap).

Requirements:
- macOS Sequoia 15.0 or later
- iPhone with iOS 18 or later
- Same Apple ID on both devices
- iPhone Mirroring enabled and connected
- pyautogui package

Setup:
1. On Mac: System Settings > Desktop & Dock > Enable iPhone Mirroring
2. Click iPhone Mirroring in Dock or Launchpad
3. Unlock iPhone once to authorize
4. Run this automation!
"""

import subprocess
import time
import os
from typing import Tuple, Optional, Dict, Any
from PIL import Image

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
        CGWindowListCreateImage,
        CGRectMake,
        kCGWindowImageDefault,
        kCGWindowListOptionIncludingWindow,
    )
    import Quartz
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False

from device_driver import DeviceDriver


class MirroringDriver(DeviceDriver):
    """iPhone Mirroring driver using pyautogui for ultra-fast automation."""

    # Window names to search for
    WINDOW_NAMES = ["iPhone Mirroring", "iPhone", "iPhone-Mirroring"]

    def __init__(
        self,
        window_name: Optional[str] = None,
        scale_factor: float = 3.0
    ):
        """
        Initialize iPhone Mirroring driver.

        Args:
            window_name: Override window name to search for
            scale_factor: Pixel to point scale (3.0 for iPhone 14 Pro)
        """
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError(
                "pyautogui is required. Install with: pip install pyautogui"
            )

        self._window_name = window_name
        self._scale_factor = scale_factor
        self._connected = False
        self._window_bounds = None  # (x, y, width, height)
        self._window_id = None
        self._content_offset = (0, 0)  # Offset for window chrome

        # Disable pyautogui fail-safe and minimize delay
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.0  # No delay between pyautogui calls!

    def connect(self) -> bool:
        """Connect to the iPhone Mirroring window."""
        try:
            if not self._find_window():
                print("Could not find iPhone Mirroring window")
                print("\nMake sure:")
                print("1. iPhone Mirroring app is open")
                print("2. Your iPhone is connected and unlocked")
                print("3. You're running macOS Sequoia 15.0+")
                return False

            self._connected = True
            print(f"Connected to iPhone Mirroring!")
            print(f"Window bounds: {self._window_bounds}")
            return True

        except Exception as e:
            print(f"Failed to connect: {e}")
            self._connected = False
            return False

    def _find_window(self) -> bool:
        """Find the iPhone Mirroring window."""
        if not QUARTZ_AVAILABLE:
            print("Quartz not available - install pyobjc-framework-Quartz")
            return False

        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )

        search_names = [self._window_name] if self._window_name else self.WINDOW_NAMES

        for window in window_list:
            owner = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')

            # Check if this is the iPhone Mirroring window
            for search_name in search_names:
                if search_name.lower() in name.lower() or \
                   search_name.lower() in owner.lower():
                    bounds = window.get('kCGWindowBounds', {})
                    self._window_bounds = (
                        int(bounds.get('X', 0)),
                        int(bounds.get('Y', 0)),
                        int(bounds.get('Width', 0)),
                        int(bounds.get('Height', 0))
                    )
                    self._window_id = window.get('kCGWindowNumber')

                    # Must be a reasonable size
                    if self._window_bounds[2] > 100 and self._window_bounds[3] > 200:
                        print(f"Found window: {owner} - {name}")
                        return True

        # Debug: list all windows
        print("\nAvailable windows:")
        for window in window_list:
            owner = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')
            if name:
                print(f"  - {owner}: {name}")

        return False

    def disconnect(self) -> None:
        """Disconnect from iPhone Mirroring."""
        self._connected = False
        self._window_bounds = None
        self._window_id = None
        print("Disconnected from iPhone Mirroring")

    def screenshot(self) -> Image.Image:
        """Capture screenshot of the mirrored iPhone screen."""
        if not self._connected:
            raise RuntimeError("Not connected")

        # Refresh window bounds
        self._find_window()

        if not self._window_bounds:
            raise RuntimeError("Window not found")

        x, y, width, height = self._window_bounds

        if QUARTZ_AVAILABLE and self._window_id:
            try:
                image_ref = CGWindowListCreateImage(
                    CGRectMake(x, y, width, height),
                    kCGWindowListOptionIncludingWindow,
                    self._window_id,
                    kCGWindowImageDefault
                )
                if image_ref:
                    img_width = Quartz.CGImageGetWidth(image_ref)
                    img_height = Quartz.CGImageGetHeight(image_ref)
                    bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)

                    data_provider = Quartz.CGImageGetDataProvider(image_ref)
                    data = Quartz.CGDataProviderCopyData(data_provider)

                    pil_image = Image.frombytes(
                        'RGBA',
                        (img_width, img_height),
                        data,
                        'raw',
                        'BGRA',
                        bytes_per_row,
                        1
                    )
                    return pil_image.convert('RGB')
            except Exception as e:
                print(f"Quartz screenshot failed: {e}")

        # Fallback
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot.convert('RGB')

    def tap(self, x: int, y: int) -> None:
        """Tap at pixel coordinates (auto-scales to window)."""
        if not self._connected:
            raise RuntimeError("Not connected")

        # Refresh window position
        self._find_window()

        if not self._window_bounds:
            raise RuntimeError("Window not found")

        # Scale pixel coords to window coords
        screen_x, screen_y = self._to_screen_coords(x, y)

        # Click instantly - no activation delay needed
        pyautogui.click(screen_x, screen_y)

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates."""
        if not self._connected:
            raise RuntimeError("Not connected")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Window not found")

        screen_x, screen_y = self._to_screen_coords(x, y)

        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.mouseDown()
        time.sleep(duration_ms / 1000.0)
        pyautogui.mouseUp()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """Perform swipe gesture (touch, hold, drag, release)."""
        if not self._connected:
            raise RuntimeError("Not connected")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Window not found")

        screen_start_x, screen_start_y = self._to_screen_coords(start_x, start_y)
        screen_end_x, screen_end_y = self._to_screen_coords(end_x, end_y)

        # Move to start position first
        pyautogui.moveTo(screen_start_x, screen_start_y)
        time.sleep(0.05)  # Small delay to ensure position

        # Press and hold
        pyautogui.mouseDown(button='left')
        time.sleep(0.05)  # Small delay to register touch

        # Drag to end position
        pyautogui.moveTo(screen_end_x, screen_end_y, duration=duration_ms / 1000.0)

        # Release
        pyautogui.mouseUp(button='left')

    def scroll(self, x: int, y: int, direction: str = "down", amount: int = 3) -> None:
        """Scroll using scroll wheel (alternative to swipe)."""
        if not self._connected:
            raise RuntimeError("Not connected")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Window not found")

        screen_x, screen_y = self._to_screen_coords(x, y)

        # Move to position first
        pyautogui.moveTo(screen_x, screen_y)

        # Scroll direction: positive = up, negative = down
        clicks = amount if direction == "up" else -amount
        pyautogui.scroll(clicks)

    def input_text(self, text: str) -> None:
        """Input text via keyboard."""
        if not self._connected:
            raise RuntimeError("Not connected")
        pyautogui.write(text, interval=0.02)

    def launch_app(self, app_identifier: str) -> None:
        """Can't launch apps via mirroring - just refresh connection."""
        self._find_window()

    def close_app(self, app_identifier: str) -> None:
        """Can't close apps via mirroring."""
        pass

    def get_screen_size(self) -> Tuple[int, int]:
        """Get window size."""
        if self._window_bounds:
            return (self._window_bounds[2], self._window_bounds[3])
        return (0, 0)

    def _to_screen_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Convert pixel coordinates to screen coordinates."""
        if not self._window_bounds:
            return (x, y)

        win_x, win_y, win_w, win_h = self._window_bounds

        # Scale from iPhone pixels to window pixels
        # iPhone 14 Pro: 1179x2556 pixels, window might be smaller
        scale_x = win_w / 1179.0  # Assuming iPhone 14 Pro width
        scale_y = win_h / 2556.0  # Assuming iPhone 14 Pro height

        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)

        screen_x = win_x + scaled_x
        screen_y = win_y + scaled_y

        return (screen_x, screen_y)

    @property
    def platform(self) -> str:
        return "mirroring"

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        return {
            "platform": "mirroring",
            "window_bounds": self._window_bounds,
            "scale_factor": self._scale_factor
        }
