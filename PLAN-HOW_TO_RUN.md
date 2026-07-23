## Phone Setup (Real Device)

> **Note:** Running on a real phone is required. Eatventure uses Google Play Games and blocks emulators.

### On the Android phone:
1. Go to **Settings → About phone**, tap **Build number** 7 times to unlock Developer Options.
2. Go to **Settings → Developer options**, enable **USB Debugging**.
3. Connect the phone to your PC via USB cable.
4. On the phone, tap **Allow** on the "Allow USB debugging?" popup.
5. Enable **Do Not Disturb** mode to prevent notification popups from interrupting the script.
6. Open Eatventure and reach the playable game screen.

### Find your device serial:
```
adb devices
```
You'll see output like:
```
List of devices attached
ABC123XYZ      device
```
`ABC123XYZ` is your serial.

### Set the serial in `.env`:
Open the `.env` file and add your serial:
```
device_serial=ABC123XYZ
DEBUG_TEMPLATE_MATCHING="0"
```
If `device_serial` is left empty, the script automatically uses the first connected ADB device.
Set `DEBUG_TEMPLATE_MATCHING="1"` only when troubleshooting template detection. It prints raw `cv2.matchTemplate` min/max values for each check, which is useful for tuning but very noisy during normal runs.

---

## What Has Been Done

1. **Python 3.13.12** installed via `winget install Python.Python.3.13`
2. **ADB** added to user PATH (`%LOCALAPPDATA%\Android\Sdk\platform-tools`)
3. **JAVA_HOME** and **ANDROID_HOME** environment variables set permanently
4. **Python virtual environment** created at `.venv` in the project root
5. **Python dependencies** installed (`requirements.txt` updated from exact old pins to `>=` minimum versions for Python 3.13 compatibility)
6. **Android command-line tools** downloaded and installed into the SDK
7. **Pixel_6_Pro_Manual** emulator (AVD) created — resolution 1440×3120, which matches the coordinates in `constants.py`
8. **`.env` file** created from `.env-sample`

## What You Still Need to Do

### 1. Fill in your Eatventure credentials and device serial

Open `.env` in the project root and fill in your account details and device serial:

```
notepad .env
```

```
email="your-email@example.com"
password="your-password"
device_serial=ABC123XYZ
DEBUG_TEMPLATE_MATCHING="0"
```

To find your device serial, run `adb devices` with your phone connected. If you leave `device_serial` empty, the script auto-detects the first connected device.


### 2. Install the Eatventure APK on the emulator

Download the Eatventure APK (v1.6.0 recommended) from [apkpure](https://apkpure.com/eatventure/com.hwqgrhhjfd.idlefastfood) or another source, then either:

- **Drag and drop** the `.apk` file onto the emulator window, or
- Run:
  ```
  adb install path\to\eatventure.apk
  ```


### 3. Run the automation script

1. Start the emulator (if not already running):
   ```
   %LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe -avd Pixel_6_Pro_Manual
   ```
2. Open the Eatventure game in the emulator and get to the playable screen.
3. Activate the virtual environment and run the script:
   ```
   cd C:\repos\auto-eatventure
   .\.venv\Scripts\activate
   python adb_autoplay.py
   ```

## Notes

- The emulator **must** be Pixel_6_Pro_Manual (1440×3120) — all tap coordinates in `constants.py` are calibrated for this resolution.
- The project was originally built for Ubuntu/Python 3.7. We updated `requirements.txt` to use `>=` minimum versions so it works with Python 3.13.
- ADB is provided by the Android SDK at `%LOCALAPPDATA%\Android\Sdk\platform-tools` and is now on your PATH.
