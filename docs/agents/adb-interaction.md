# ADB Interaction

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

All device interaction happens through **Android Debug Bridge (ADB)** via the `adbutils` Python library. The `Device` class in `device.py` encapsulates all ADB communication.

## Device Connection

`Device.__init__()` at `device.py`:

```python
serial = os.getenv("device_serial", "").strip()
if serial:
    self.device = adb.device(serial=serial)
else:
    self.device = adb.device_list()[0]  # first connected
```

- Set `device_serial` in `.env` to target a specific device/emulator
- Leave empty to auto-select the first connected device

## Input Commands

All methods are on the `Device` class in `device.py`:

### Tap

```python
def click(self, coords):
    # Accepts dict {x, y} or list [x, y]
    self.device.shell(f"input tap {x} {y}")
```

### Long Press

```python
def click_and_hold(self, x, y, hold_duration=1000):
    self.device.shell(f'input swipe {x} {y} {x} {y} {hold_duration}')
```

### Swipe

```python
def swipe(self, start, end):
    self.device.swipe(start['x'], start['y'], end['x'], end['y'])
```

### Text Input

```python
def input_text(self, text):
    escaped_text = text.replace(" ", "%s").replace("&", "\\&")...
    self.device.shell(f"input text '{escaped_text}'")
```

## Screenshot Capture

`Device.capture_screenshot()` at `device.py`:

- **Windows**: `adb shell screencap -p` with `\r\n` -> `\n` fix
- **Linux/macOS**: `adb exec-out screencap -p` (raw binary)

After capture, stores three representations on the instance:
- `current_cv2_sc` -- BGR numpy array
- `current_cv2_sc_grayscale` -- grayscale numpy array
- `current_cv2_sc_bgr2hsv` -- HSV numpy array

## App Lifecycle

```python
def start_app(self):
    self.device.shell(f"monkey -p {self.package_name} -c ... 1")

def close_app(self):
    self.device.shell(f"am force-stop {self.package_name}")
```

Package: `com.hwqgrhhjfd.idlefastfood`

## Platform Differences

| Platform | Screenshot Method | Notes |
|----------|-------------------|-------|
| Windows | `adb shell screencap -p` + `\r\n` fix | ADB corrupts binary on Windows |
| Linux/macOS | `adb exec-out screencap -p` | Raw binary output |

## Prerequisites

- ADB installed and on `PATH`
- Device has USB debugging enabled
- Emulator or physical device connected (`adb devices` shows it) — note: emulators can run the bot, but Eatventure's Google Play Games login is blocked on emulators, so a physical device is needed to actually sign in and keep progress
- Game installed: `com.hwqgrhhjfd.idlefastfood`
