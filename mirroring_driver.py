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

        # Enable pyautogui fail-safe (move mouse to top-left corner to stop)
        pyautogui.FAILSAFE = True
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
                    new_bounds = (
                        int(bounds.get('X', 0)),
                        int(bounds.get('Y', 0)),
                        int(bounds.get('Width', 0)),
                        int(bounds.get('Height', 0))
                    )
                    self._window_id = window.get('kCGWindowNumber')

                    # Must be a reasonable size
                    if new_bounds[2] > 100 and new_bounds[3] > 200:
                        # Only print if window changed
                        if self._window_bounds != new_bounds:
                            print(f"Window: {new_bounds[2]}x{new_bounds[3]} at ({new_bounds[0]}, {new_bounds[1]})")
                        self._window_bounds = new_bounds
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

    # Target resolution for coordinates (iPhone 14 Pro)
    # Templates and constants use this resolution
    TARGET_WIDTH = 1179
    TARGET_HEIGHT = 2556

    def screenshot(self) -> Image.Image:
        """Capture screenshot of the mirrored iPhone screen at native window resolution.

        Note: Returns native window size (not upscaled). The automation script
        should scale templates down to match, then scale coordinates back up.
        """
        if not self._connected:
            raise RuntimeError("Not connected")

        # Refresh window bounds
        self._find_window()

        if not self._window_bounds:
            raise RuntimeError("Window not found")

        x, y, width, height = self._window_bounds
        pil_image = None

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
                    pil_image = pil_image.convert('RGB')
            except Exception as e:
                print(f"Quartz screenshot failed: {e}")

        # Fallback to pyautogui
        if pil_image is None:
            pil_image = pyautogui.screenshot(region=(x, y, width, height))
            pil_image = pil_image.convert('RGB')

        # DON'T upscale - return native window size for better template matching
        # Upscaling creates blur that breaks template matching
        # The automation script will scale templates/coordinates as needed
        return pil_image

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

        # Bounds check - ensure click is within window
        win_x, win_y, win_w, win_h = self._window_bounds
        if not (win_x <= screen_x <= win_x + win_w and win_y <= screen_y <= win_y + win_h):
            print(f"[WARN] Click ({screen_x}, {screen_y}) outside window bounds, skipping")
            return

        # Move first, pause, then explicit down/up to prevent scroll
        pyautogui.moveTo(screen_x, screen_y)
        time.sleep(0.03)  # Pause to ensure position is stable
        # Use explicit mouseDown/Up instead of click to prevent any drag
        pyautogui.mouseDown(button='left')
        time.sleep(0.01)  # Very short press
        pyautogui.mouseUp(button='left')

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates."""
        if not self._connected:
            raise RuntimeError("Not connected")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Window not found")

        screen_x, screen_y = self._to_screen_coords(x, y)

        # Bounds check
        win_x, win_y, win_w, win_h = self._window_bounds
        if not (win_x <= screen_x <= win_x + win_w and win_y <= screen_y <= win_y + win_h):
            print(f"[WARN] Long press ({screen_x}, {screen_y}) outside window bounds, skipping")
            return

        pyautogui.moveTo(screen_x, screen_y)
        time.sleep(0.03)  # Pause to ensure position
        pyautogui.mouseDown(button='left')
        time.sleep(duration_ms / 1000.0)
        pyautogui.mouseUp(button='left')

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
        """Convert iPhone pixel coordinates to Mac screen coordinates."""
        if not self._window_bounds:
            return (x, y)

        win_x, win_y, win_w, win_h = self._window_bounds

        # Scale from iPhone resolution (1179x2556) to window size
        scale_x = win_w / float(self.TARGET_WIDTH)
        scale_y = win_h / float(self.TARGET_HEIGHT)

        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)

        # Add window offset to get Mac screen coordinates
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
