"""
PlayCover Device Driver

Uses pyautogui to automate iOS apps running in PlayCover on Apple Silicon Macs.
Requires:
- macOS on Apple Silicon (M1/M2/M3)
- PlayCover installed with the game
- pyautogui and pillow packages

PlayCover runs iOS apps in a window, so we use standard Mac automation.
"""

import subprocess
import time
from typing import Tuple, Optional, Dict, Any
from PIL import Image

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from AppKit import NSWorkspace, NSApplicationActivateIgnoringOtherApps
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


class PlayCoverDriver(DeviceDriver):
    """PlayCover driver using pyautogui for Mac desktop automation."""

    # Default app name as it appears in PlayCover
    DEFAULT_APP_NAME = "Idle Cooking Tycoon"

    def __init__(
        self,
        app_name: str = DEFAULT_APP_NAME,
        window_scale: float = 1.0
    ):
        """
        Initialize PlayCover driver.

        Args:
            app_name: Name of the app as it appears in the window title
            window_scale: Scale factor for coordinate mapping (default 1.0)
        """
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError(
                "pyautogui is required for PlayCover support. "
                "Install with: pip install pyautogui"
            )

        self._app_name = app_name
        self._window_scale = window_scale
        self._connected = False
        self._window_bounds = None  # (x, y, width, height)
        self._window_id = None

        # Disable pyautogui fail-safe for automation
        pyautogui.FAILSAFE = False
        # Set pause between actions
        pyautogui.PAUSE = 0.1

    def connect(self) -> bool:
        """Connect to the PlayCover app window."""
        try:
            # Find the PlayCover app window
            if not self._find_window():
                print(f"Could not find window for '{self._app_name}'")
                print("Make sure the app is running in PlayCover")
                return False

            self._connected = True
            print(f"Connected to PlayCover app: {self._app_name}")
            print(f"Window bounds: {self._window_bounds}")
            return True

        except Exception as e:
            print(f"Failed to connect to PlayCover app: {e}")
            self._connected = False
            return False

    def _find_window(self) -> bool:
        """Find the app window and get its bounds."""
        if QUARTZ_AVAILABLE:
            return self._find_window_quartz()
        else:
            return self._find_window_applescript()

    def _find_window_quartz(self) -> bool:
        """Find window using Quartz (more accurate)."""
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )

        for window in window_list:
            owner = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')

            # PlayCover apps run under their own name or PlayCover
            if self._app_name.lower() in name.lower() or \
               self._app_name.lower() in owner.lower():
                bounds = window.get('kCGWindowBounds', {})
                self._window_bounds = (
                    int(bounds.get('X', 0)),
                    int(bounds.get('Y', 0)),
                    int(bounds.get('Width', 0)),
                    int(bounds.get('Height', 0))
                )
                self._window_id = window.get('kCGWindowNumber')

                if self._window_bounds[2] > 100 and self._window_bounds[3] > 100:
                    return True

        return False

    def _find_window_applescript(self) -> bool:
        """Find window using AppleScript (fallback method)."""
        script = f'''
        tell application "System Events"
            set appList to every process whose name contains "{self._app_name}"
            if (count of appList) > 0 then
                set theApp to item 1 of appList
                set appName to name of theApp
                tell process appName
                    set frontWindow to front window
                    set winPos to position of frontWindow
                    set winSize to size of frontWindow
                    return (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                end tell
            end if
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) == 4:
                    self._window_bounds = tuple(int(p) for p in parts)
                    return True
        except Exception as e:
            print(f"AppleScript error: {e}")

        return False

    def disconnect(self) -> None:
        """Disconnect from the app."""
        self._connected = False
        self._window_bounds = None
        self._window_id = None
        print("Disconnected from PlayCover app")

    def screenshot(self) -> Image.Image:
        """Capture screenshot of the app window."""
        if not self._connected:
            raise RuntimeError("Not connected to app")

        # Refresh window bounds in case window moved
        self._find_window()

        if not self._window_bounds:
            raise RuntimeError("Could not find app window")

        x, y, width, height = self._window_bounds

        if QUARTZ_AVAILABLE and self._window_id:
            # Use Quartz for more accurate window capture
            try:
                image_ref = CGWindowListCreateImage(
                    CGRectMake(x, y, width, height),
                    kCGWindowListOptionIncludingWindow,
                    self._window_id,
                    kCGWindowImageDefault
                )
                if image_ref:
                    width = Quartz.CGImageGetWidth(image_ref)
                    height = Quartz.CGImageGetHeight(image_ref)
                    bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)

                    # Get image data
                    data_provider = Quartz.CGImageGetDataProvider(image_ref)
                    data = Quartz.CGDataProviderCopyData(data_provider)

                    # Convert to PIL Image
                    pil_image = Image.frombytes(
                        'RGBA',
                        (width, height),
                        data,
                        'raw',
                        'BGRA',
                        bytes_per_row,
                        1
                    )
                    return pil_image.convert('RGB')
            except Exception as e:
                print(f"Quartz screenshot failed: {e}, falling back to pyautogui")

        # Fallback to pyautogui region screenshot
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot.convert('RGB')

    def tap(self, x: int, y: int) -> None:
        """Tap at coordinates within the app window."""
        if not self._connected:
            raise RuntimeError("Not connected to app")

        # Refresh window bounds
        self._find_window()

        if not self._window_bounds:
            raise RuntimeError("Could not find app window")

        # Convert app coordinates to screen coordinates
        screen_x, screen_y = self._to_screen_coords(x, y)

        print(f"[TAP] app({x}, {y}) -> screen({screen_x}, {screen_y})")

        # Bring app to front and click
        self._activate_app()
        pyautogui.click(screen_x, screen_y)

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates within the app window."""
        if not self._connected:
            raise RuntimeError("Not connected to app")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Could not find app window")

        screen_x, screen_y = self._to_screen_coords(x, y)

        self._activate_app()

        # Move to position, press, wait, release
        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.mouseDown()
        time.sleep(duration_ms / 1000.0)
        pyautogui.mouseUp()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """Perform a swipe gesture within the app window."""
        if not self._connected:
            raise RuntimeError("Not connected to app")

        self._find_window()
        if not self._window_bounds:
            raise RuntimeError("Could not find app window")

        screen_start_x, screen_start_y = self._to_screen_coords(start_x, start_y)
        screen_end_x, screen_end_y = self._to_screen_coords(end_x, end_y)

        self._activate_app()

        # Perform drag operation
        pyautogui.moveTo(screen_start_x, screen_start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(screen_end_x, screen_end_y, duration=duration_ms / 1000.0)
        pyautogui.mouseUp()

    def input_text(self, text: str) -> None:
        """Input text using keyboard."""
        if not self._connected:
            raise RuntimeError("Not connected to app")

        self._activate_app()
        pyautogui.write(text, interval=0.05)

    def launch_app(self, app_identifier: str) -> None:
        """Launch the app in PlayCover."""
        if not self._connected:
            # Try to launch via PlayCover or just activate if already running
            pass

        # Bring app to front
        self._activate_app()
        time.sleep(2)

        # Refresh connection
        self._find_window()

    def close_app(self, app_identifier: str) -> None:
        """Close the app."""
        # Use Cmd+Q to quit
        self._activate_app()
        pyautogui.hotkey('command', 'q')

    def get_screen_size(self) -> Tuple[int, int]:
        """Get the app window size."""
        if self._window_bounds:
            return (self._window_bounds[2], self._window_bounds[3])
        return (0, 0)

    def _to_screen_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Convert app window coordinates to screen coordinates."""
        if not self._window_bounds:
            return (x, y)

        win_x, win_y, win_w, win_h = self._window_bounds

        # Apply any coordinate scaling
        scaled_x = int(x * self._window_scale)
        scaled_y = int(y * self._window_scale)

        # Add window offset
        screen_x = win_x + scaled_x
        screen_y = win_y + scaled_y

        return (screen_x, screen_y)

    def _activate_app(self) -> None:
        """Bring the app window to front."""
        if QUARTZ_AVAILABLE:
            try:
                workspace = NSWorkspace.sharedWorkspace()
                apps = workspace.runningApplications()
                for app in apps:
                    if self._app_name.lower() in app.localizedName().lower():
                        app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
                        time.sleep(0.1)
                        return
            except Exception:
                pass

        # Fallback to AppleScript
        script = f'''
        tell application "{self._app_name}"
            activate
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=2)
            time.sleep(0.1)
        except Exception:
            pass

    @property
    def platform(self) -> str:
        return "playcover"

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_device_info(self) -> Dict[str, Any]:
        """Get device/window information."""
        return {
            "platform": "playcover",
            "app_name": self._app_name,
            "window_bounds": self._window_bounds,
            "window_scale": self._window_scale
        }
