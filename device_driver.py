"""
Device Driver Abstraction Layer

This module provides an abstract interface for device interaction,
allowing the automation to work with both Android (ADB) and iOS (Appium) devices.
"""

from abc import ABC, abstractmethod
from PIL import Image
from typing import Tuple, Optional, Dict, Any


class DeviceDriver(ABC):
    """Abstract base class for device drivers."""

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the device.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the device."""
        pass

    @abstractmethod
    def screenshot(self) -> Image.Image:
        """
        Capture a screenshot from the device.

        Returns:
            PIL.Image: Screenshot as a PIL Image object.
        """
        pass

    @abstractmethod
    def tap(self, x: int, y: int) -> None:
        """
        Perform a tap at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        pass

    @abstractmethod
    def tap_and_hold(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """
        Perform a long press at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            duration_ms: Hold duration in milliseconds
        """
        pass

    @abstractmethod
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500) -> None:
        """
        Perform a swipe gesture.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration_ms: Swipe duration in milliseconds
        """
        pass

    @abstractmethod
    def input_text(self, text: str) -> None:
        """
        Input text on the device.

        Args:
            text: Text to input
        """
        pass

    @abstractmethod
    def launch_app(self, app_identifier: str) -> None:
        """
        Launch an application.

        Args:
            app_identifier: Package name (Android) or bundle ID (iOS)
        """
        pass

    @abstractmethod
    def close_app(self, app_identifier: str) -> None:
        """
        Force close an application.

        Args:
            app_identifier: Package name (Android) or bundle ID (iOS)
        """
        pass

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the device screen size.

        Returns:
            Tuple of (width, height) in pixels.
        """
        pass

    @property
    @abstractmethod
    def platform(self) -> str:
        """Return the platform name ('android' or 'ios')."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if device is connected."""
        pass
