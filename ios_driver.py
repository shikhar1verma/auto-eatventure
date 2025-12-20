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
import time
from typing import Tuple, Optional, Dict, Any
from PIL import Image

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

    def __init__(
        self,
        udid: Optional[str] = None,
        appium_url: str = DEFAULT_APPIUM_URL,
        bundle_id: str = "com.hwqgrhhjfd.idlefastfood",
        wda_bundle_id: str = "com.facebook.WebDriverAgentRunner.xctrunner",
        device_name: str = "iPhone",
        platform_version: str = "17.0"
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

            # Use existing WebDriverAgent
            options.use_prebuilt_wda = True
            options.wda_launch_timeout = 120000
            options.wda_connection_timeout = 240000

            # Set bundle ID for the game
            options.bundle_id = self._bundle_id

            # Set custom WDA bundle ID if provided
            if self._wda_bundle_id:
                options.updated_wda_bundle_id = self._wda_bundle_id

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

        return pil_image

    def tap(self, x: int, y: int) -> None:
        """Tap at coordinates."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        # Use W3C Actions for precise tap
        self._driver.tap([(x, y)])

    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at coordinates."""
        if not self._connected:
            raise RuntimeError("Device not connected")

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
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration_ms / 1000.0)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """Perform swipe gesture."""
        if not self._connected:
            raise RuntimeError("Device not connected")

        self._driver.swipe(start_x, start_y, end_x, end_y, duration_ms)

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
