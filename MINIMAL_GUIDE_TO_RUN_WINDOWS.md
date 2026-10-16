# Minimal Guide to Run

## Prerequisites

### 1. Python 3.13
```powershell
winget install Python.Python.3.13
```

### 2. ADB (Android Debug Bridge)
Requires [Chocolatey](https://chocolatey.org/install) to be installed first, then run as Administrator:
```powershell
choco install adb
```
This installs only the platform-tools (adb.exe) and adds them to PATH automatically.

---

## Project Setup

### 3. Clone the repository
```powershell
git clone <repo-url>
cd auto-eatventure
"git checkout correct branch"
```

### 4. Create the `.env` file
```powershell
copy .env-sample .env
notepad .env
```
Fill in your device serial (and credentials if needed) When it is only connected device it is not needed to fill it:
```
device_serial=ABC123XYZ
DEBUG_TEMPLATE_MATCHING="0"
```

---

## Phone Setup

### 6. Enable USB Debugging on your Android phone
1. Go to **Settings → About phone**, tap **Build number** 7 times to unlock Developer Options.
2. Go to **Settings → Developer options**, enable **USB Debugging**.
3. Connect phone to PC via USB.
4. Tap **Allow** on the "Allow USB debugging?" popup on the phone.

### 7. Find your device serial
```powershell
adb devices
```
Output example:
```
List of devices attached
ABC123XYZ      device
```
Use `ABC123XYZ` as `device_serial` in `.env`. If left empty, the script auto-detects the first connected device.

### 8. Enable Do Not Disturb on the phone
Prevents notification popups from interrupting the script.

### 9. Open Eatventure and get to the playable game screen.

---

## Run

### First time only — allow running scripts (PowerShell execution policy)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### First time only — create virtual environment and install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Every time
```powershell
start.bat
```

---

## Notes

- **Emulator does not work** — Eatventure uses Google Play Games and blocks emulators(you cannot login). A real physical Android device is required.
- All tap coordinates are calibrated at 1220x2712 (`coords/reference.py`) and scaled to your phone's resolution. On a phone with a different aspect ratio some of them may need adjustment.
