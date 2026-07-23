# Minimal Guide to Run

## Prerequisites

### 1. Python 3.13
```bash
sudo apt install python3.13
```

### 2. ADB (Android Debug Bridge)
```bash
sudo apt install adb
```

---

## Project Setup

### 3. Clone the repository
```bash
git clone <repo-url>
cd auto-eatventure
# git checkout correct-branch
```

### 4. Create the `.env` file
```bash
cp .env-sample .env
nano .env
```
Fill in your device serial (and credentials if needed). When it is only connected device it is not needed to fill it:
```
device_serial=ABC123XYZ
DEBUG_TEMPLATE_MATCHING="0"
```

---

## Phone Setup

### 5. Enable USB Debugging on your Android phone
1. Go to **Settings → About phone**, tap **Build number** 7 times to unlock Developer Options.
2. Go to **Settings → Developer options**, enable **USB Debugging**.
3. Connect phone to PC via USB.
4. Tap **Allow** on the "Allow USB debugging?" popup on the phone.

### 6. Find your device serial
```bash
adb devices
```
Output example:
```
List of devices attached
ABC123XYZ      device
```
Use `ABC123XYZ` as `device_serial` in `.env`. If left empty, the script auto-detects the first connected device.

### 7. Enable Do Not Disturb on the phone
Prevents notification popups from interrupting the script.

### 8. Open Eatventure and get to the playable game screen.

---

## Run

### First time only — create virtual environment and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x start.sh
```

### Every time
```bash
./start.sh
```

---

## Notes

- **Emulator does not work** — Eatventure uses Google Play Games and blocks emulators (you cannot login). A real physical Android device is required.
- All tap coordinates are calibrated for a specific screen resolution. If your phone has a different resolution, coordinates in `constants.py` may need adjustment.
