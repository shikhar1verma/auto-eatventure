"""
Configuration module for Auto-Eatventure.

Handles platform selection and configuration loading.
"""

import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Platform(Enum):
    ANDROID = "android"
    IOS = "ios"


class Config:
    """Configuration manager for the automation."""

    def __init__(self):
        # Platform selection - can be set via environment variable
        platform_str = os.getenv("PLATFORM", "android").lower()
        self.platform = Platform(platform_str)

        # Android settings
        self.android_device_serial: Optional[str] = os.getenv("ANDROID_SERIAL")
        self.android_package = os.getenv(
            "ANDROID_PACKAGE", "com.hwqgrhhjfd.idlefastfood")

        # iOS settings
        self.ios_udid: Optional[str] = os.getenv("IOS_UDID")
        self.ios_bundle_id = os.getenv(
            "IOS_BUNDLE_ID", "com.hwqgrhhjfd.idlefastfood")
        self.ios_device_name = os.getenv("IOS_DEVICE_NAME", "iPhone")
        self.ios_platform_version = os.getenv("IOS_PLATFORM_VERSION", "17.0")
        self.appium_url = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")
        self.wda_bundle_id = os.getenv(
            "WDA_BUNDLE_ID", "com.yourname.WebDriverAgentRunner")
        # Use iOS Simulator instead of physical device
        self.ios_use_simulator = os.getenv("IOS_USE_SIMULATOR", "false").lower() == "true"

        # Cloud save credentials
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")

    def get_app_identifier(self) -> str:
        """Get the app identifier for the current platform."""
        if self.platform == Platform.IOS:
            return self.ios_bundle_id
        return self.android_package

    def get_constants_module(self):
        """Import and return the appropriate constants module."""
        if self.platform == Platform.IOS:
            import constants_ios as loc
        else:
            import constants as loc
        return loc

    def create_driver(self):
        """Create and return the appropriate device driver."""
        if self.platform == Platform.IOS:
            from ios_driver import IOSDriver
            return IOSDriver(
                udid=self.ios_udid,
                appium_url=self.appium_url,
                bundle_id=self.ios_bundle_id,
                wda_bundle_id=self.wda_bundle_id,
                device_name=self.ios_device_name,
                platform_version=self.ios_platform_version,
                use_simulator=self.ios_use_simulator
            )
        else:
            from android_driver import AndroidDriver
            return AndroidDriver(device_serial=self.android_device_serial)

    def __str__(self):
        return f"Config(platform={self.platform.value})"


# Default global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def set_platform(platform: Platform) -> None:
    """Change the platform at runtime."""
    config.platform = platform
