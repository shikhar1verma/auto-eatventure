# ADB Interaction

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

All device interaction happens through **Android Debug Bridge (ADB)** via the `adbutils` Python library. The `Device` class in `android/device.py` (module paths are relative to `src/auto_eatventure/`) encapsulates all ADB communication. Actions use it as `game.device`.

## Device Connection

`Device.__init__(serial)` in `android/device.py`, called from `main.py` with `config.DEVICE_SERIAL`:

```python
if serial:
  self._adb = adb.device(serial=serial)
else:
  self._adb = adb.device_list()[0]  # first connected, with a warning
```

- Set `device_serial` in `.env` to target a specific device/emulator
- Leave empty to auto-select the first connected device
- No device connected raises `RuntimeError`

`Device.screen_size()` returns `(width, height)` parsed from `wm size`.

## Input Commands

All methods are on the `Device` class in `android/device.py`. Positions are `Point` / `Swipe` from `coords/geometry.py`.

### Tap

```python
def tap(self, point):
  self._adb.shell(f'input tap {point.x} {point.y}')
```

### Long Press

```python
def long_press(self, point, duration_ms):
  self._adb.shell(f'input swipe {point.x} {point.y} '
                  f'{point.x} {point.y} {duration_ms}')
```

### Swipe

```python
def swipe(self, swipe):
  self._adb.swipe(swipe.start.x, swipe.start.y,
                  swipe.end.x, swipe.end.y)
```

## Screenshot Capture

`Device.screenshot()` in `android/device.py` returns the screen as a BGR numpy array:

- **Windows**: `adb shell screencap -p` with `\r\n` -> `\n` fix
- **Linux/macOS**: `adb exec-out screencap -p` (raw binary)

`Screen.capture()` (`vision/screen.py`) calls it and keeps three representations:
- `screen.bgr` -- BGR numpy array
- `screen.gray` -- grayscale numpy array
- `screen.hsv` -- HSV numpy array

## App Lifecycle

```python
def start_app(self):
  self._adb.shell(f'monkey -p {GAME_PACKAGE} '
                  '-c android.intent.category.LAUNCHER 1')

def close_app(self):
  self._adb.shell(f'am force-stop {GAME_PACKAGE}')
```

Package: `com.hwqgrhhjfd.idlefastfood` (`GAME_PACKAGE`). `start_app()` launches the game or brings it to the foreground; it does not restart a running game. `close_app()` is currently unused.

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
