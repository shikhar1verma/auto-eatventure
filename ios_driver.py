"""
iOS Device Driver

Uses Appium with XCUITest/WebDriverAgent to interact with iOS devices.
Requires:
- macOS with Xcode installed
- WebDriverAgent built and signed
- Appium server running
"""

import base64
import io
import os
import time
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw

try:
    from appium import webdriver
    from appium.webdriver.common.appiumby import AppiumBy
    from appium.options.ios import XCUITestOptions
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

from device_driver import DeviceDriver


class IOSDriver(DeviceDriver):
    """iOS device driver using Appium/WebDriverAgent."""

    # Default Appium server URL
    DEFAULT_APPIUM_URL = "http://127.0.0.1:4723"

    # Scale factor for converting pixels to points (iPhone 14 Pro = 3x)
    SCALE_FACTOR = 3.0

    # Debug mode - saves screenshots with tap markers (disable for speed)
    DEBUG_TAPS = os.getenv("DEBUG_TAPS", "false").lower() == "true"
    DEBUG_DIR = "debug_taps"

    def __init__(
        self,
        udid: Optional[str] = None,
        appium_url: str = DEFAULT_APPIUM_URL,
        bundle_id: str = "com.hwqgrhhjfd.idlefastfood",
        wda_bundle_id: str = "com.facebook.WebDriverAgentRunner.xctrunner",
        device_name: str = "iPhone",
        platform_version: str = "17.0",
        scale_factor: float = 3.0,
        use_simulator: bool = False
    ):
        """
        Initialize iOS driver.

        Args:
            udid: Device UDID (optional, auto-detects if not provided)
            appium_url: Appium server URL
            bundle_id: App bundle identifier
            wda_bundle_id: WebDriverAgent bundle ID (update if you changed it)
            device_name: Device name for capabilities
            platform_version: iOS version
            scale_factor: Pixel to point scale factor (3.0 for iPhone 14 Pro)
            use_simulator: If True, use iOS Simulator instead of physical device
        """
        if not APPIUM_AVAILABLE:
            raise ImportError(
                "Appium-Python-Client is required for iOS support. "
                "Install with: pip install Appium-Python-Client"
            )

        self._appium_url = appium_url
        self._bundle_id = bundle_id
        self._wda_bundle_id = wda_bundle_id
        self._device_name = device_name
        self._platform_version = platform_version
        self._udid = udid
        self._scale_factor = scale_factor
        self._use_simulator = use_simulator

        self._driver = None
        self._connected = False
        self._screen_size = None

    def connect(self) -> bool:
        """Connect to iOS device via Appium/WebDriverAgent."""
        try:
            options = XCUITestOptions()
            options.platform_name = "iOS"
            options.platform_version = self._platform_version
            options.device_name = self._device_name
            options.automation_name = "XCUITest"

            # Don't reset the app - we want to continue existing game
            options.no_reset = True
            options.full_reset = False

            if self._use_simulator:
                # Simulator mode - Appium manages WDA automatically
                print("Using iOS Simulator mode")
                options.set_capability("isSimulator", True)
            else:
                # Physical device mode - connect to WDA running from Xcode
                print("Using physical device mode")
                options.set_capability("webDriverAgentUrl", "http://localhost:8100")
                options.use_prebuilt_wda = True
                options.use_new_wda = False
                options.wda_launch_timeout = 120000
                options.wda_connection_timeout = 240000
                options.wda_local_port = 8101

                # Set custom WDA bundle ID if provided
                if self._wda_bundle_id:
                    options.updated_wda_bundle_id = self._wda_bundle_id

            # Skip log capture for faster performance
            options.set_capability("skipLogCapture", True)
            options.set_capability("waitForQuiescence", False)

            # Set bundle ID for the game
            options.bundle_id = self._bundle_id

            # Set UDID if provided
            if self._udid:
                options.udid = self._udid

            # Don't start the app automatically - we'll control that
            options.auto_launch = False

            # Increase timeouts for slow operations
            options.new_command_timeout = 300

            print(f"Connecting to iOS device via Appium at {self._appium_url}...")
            print("This may take a minute on first connection...")

            self._driver = webdriver.Remote(
                command_executor=self._appium_url,
                options=options
            )

            self._connected = True

            # Cache screen size
            self._update_screen_size()

            print(f"Connected to iOS device: {self._device_name}")
            print(f"Screen size: {self._screen_size}")
            return True

        except Exception as e:
            print(f"Failed to connect to iOS device: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure Appium server is running: appium")
            print("2. Make sure your device is connected and trusted")
            print("3. Make sure WebDriverAgent is installed on device")
            print("4. Check that the bundle IDs are correct")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
        self._driver = None
        self._connected = False
        print("Disconnected from iOS device")

    def screenshot(self) -> Image.Image:
        """Capture screenshot from iOS device."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Get screenshot as base64
        screenshot_base64 = self._driver.get_screenshot_as_base64()

        # Convert to PIL Image
        screenshot_bytes = base64.b64decode(screenshot_base64)
        pil_image = Image.open(io.BytesIO(screenshot_bytes))
        pil_image = pil_image.convert("RGB")

        # Store for debug overlay
        if self.DEBUG_TAPS:
            self._last_screenshot = pil_image.copy()

        return pil_image

    def _save_debug_screenshot(self, pixel_x: int, pixel_y: int, point_x: int, point_y: int) -> None:
        """Save screenshot with tap marker for debugging."""
        if not self._last_screenshot:
            return

        try:
            # Create debug directory
            os.makedirs(self.DEBUG_DIR, exist_ok=True)

            # Copy screenshot and draw markers
            debug_img = self._last_screenshot.copy()
            draw = ImageDraw.Draw(debug_img)

            # Draw crosshair at PIXEL coordinates (where we detected the target)
            # Blue = detected position
            cross_size = 40
            draw.line([(pixel_x - cross_size, pixel_y), (pixel_x + cross_size, pixel_y)], fill='blue', width=5)
            draw.line([(pixel_x, pixel_y - cross_size), (pixel_x, pixel_y + cross_size)], fill='blue', width=5)
            draw.ellipse([(pixel_x - 30, pixel_y - 30), (pixel_x + 30, pixel_y + 30)], outline='blue', width=5)

            # Draw where the TAP will actually land (convert point back to pixel)
            actual_pixel_x = int(point_x * self._scale_factor)
            actual_pixel_y = int(point_y * self._scale_factor)

            # Red = actual tap position
            draw.line([(actual_pixel_x - cross_size, actual_pixel_y), (actual_pixel_x + cross_size, actual_pixel_y)], fill='red', width=5)
            draw.line([(actual_pixel_x, actual_pixel_y - cross_size), (actual_pixel_x, actual_pixel_y + cross_size)], fill='red', width=5)
            draw.ellipse([(actual_pixel_x - 25, actual_pixel_y - 25), (actual_pixel_x + 25, actual_pixel_y + 25)], outline='red', width=5)

            # Add text label
            label = f"Detected: ({pixel_x}, {pixel_y}) | Tap: ({point_x}, {point_y}) → pixel({actual_pixel_x}, {actual_pixel_y})"
            draw.rectangle([(10, 10), (len(label) * 12 + 20, 50)], fill='black')
            draw.text((15, 15), label, fill='white')

            # Save with timestamp
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
            filename = f"{self.DEBUG_DIR}/tap_{timestamp}_{pixel_x}_{pixel_y}.png"
            debug_img.save(filename)
            print(f"[DEBUG] Saved tap screenshot: {filename}")

        except Exception as e:
            print(f"[DEBUG] Failed to save debug screenshot: {e}")

    # Y offset in points to adjust for status bar/Dynamic Island (tune if taps are off)
    TAP_Y_OFFSET = 0  # Start with 0, adjust if needed

    # Store last screenshot for debug overlay
    _last_screenshot = None

    def tap(self, x: int, y: int) -> None:
        """Tap at coordinates (automatically converts pixels to points)."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Convert pixel coordinates to points for iOS
        # Screenshots are in pixels but Appium taps use points
        point_x = int(x / self._scale_factor)
        point_y = int(y / self._scale_factor) + self.TAP_Y_OFFSET

        print(f"[TAP] pixel({x}, {y}) → point({point_x}, {point_y})")

        # Save debug screenshot with tap marker
        if self.DEBUG_TAPS and self._last_screenshot:
            self._save_debug_screenshot(x, y, point_x, point_y)

        # Use W3C Actions for precise tap
        self._driver.tap([(point_x, point_y)])

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates (automatically converts pixels to points)."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Convert pixel coordinates to points for iOS
        point_x = int(x / self._scale_factor)
        point_y = int(y / self._scale_factor) + self.TAP_Y_OFFSET

        # Use touch action for long press
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.actions import interaction
        from selenium.webdriver.common.actions.action_builder import ActionBuilder
        from selenium.webdriver.common.actions.pointer_input import PointerInput

        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(
            self._driver,
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
        )
        actions.w3c_actions.pointer_action.move_to_location(point_x, point_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration_ms / 1000.0)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """Perform swipe gesture (automatically converts pixels to points)."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Convert pixel coordinates to points for iOS
        start_x_pt = int(start_x / self._scale_factor)
        start_y_pt = int(start_y / self._scale_factor)
        end_x_pt = int(end_x / self._scale_factor)
        end_y_pt = int(end_y / self._scale_factor)

        self._driver.swipe(start_x_pt, start_y_pt, end_x_pt, end_y_pt, duration_ms)

    def input_text(self, text: str) -> None:
        """Input text on device."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # For iOS, we can use the keyboard directly
        # This works when a text field is focused
        self._driver.execute_script('mobile: type', {'text': text})

    def launch_app(self, app_identifier: str) -> None:
        """Launch app by bundle ID."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._driver.activate_app(app_identifier)
        # Give the app time to launch
        time.sleep(2)

    def close_app(self, app_identifier: str) -> None:
        """Force close app by bundle ID."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._driver.terminate_app(app_identifier)

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

        window_size = self._driver.get_window_size()
        self._screen_size = (window_size['width'], window_size['height'])

    @property
    def platform(self) -> str:
        return "ios"

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def driver(self):
        """Return the underlying Appium driver for advanced usage."""
        return self._driver

    @property
    def bundle_id(self) -> str:
        """Return the app bundle ID."""
        return self._bundle_id

    def is_app_running(self, bundle_id: Optional[str] = None) -> bool:
        """Check if app is currently running."""
        if not self._connected:
            return False

        bid = bundle_id or self._bundle_id
        state = self._driver.query_app_state(bid)
        # State 4 = running in foreground
        return state == 4

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        return {
            "platform": "ios",
            "platform_version": self._platform_version,
            "device_name": self._device_name,
            "screen_size": self._screen_size,
            "udid": self._udid
        }
