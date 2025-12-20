# iOS Setup Guide for Auto-Eatventure

This guide walks you through setting up Auto-Eatventure on iOS using Appium and WebDriverAgent with a **free Apple Developer account**.

## Prerequisites

- Mac with macOS 12+ (Monterey or later recommended)
- Xcode 14+ (free from App Store)
- iPhone with iOS 15+ connected via USB
- Eatventure installed on your iPhone
- Python 3.8+

## Overview of Steps

1. Install Xcode and command line tools
2. Install Node.js and Appium
3. Build and install WebDriverAgent
4. Configure the automation
5. Capture iOS template images
6. Calibrate coordinates and colors
7. Run the automation

---

## Step 1: Install Xcode and Command Line Tools

### 1.1 Install Xcode

1. Open **App Store** on your Mac
2. Search for "Xcode"
3. Click **Get** / **Install** (it's ~12GB, this takes a while)
4. Once installed, open Xcode and accept the license agreement

### 1.2 Install Command Line Tools

Open Terminal and run:

```bash
xcode-select --install
```

Click **Install** when prompted.

---

## Step 2: Install Node.js and Appium

### 2.1 Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2.2 Install Node.js

```bash
brew install node
```

Verify installation:
```bash
node --version  # Should show v18+ or similar
npm --version   # Should show 9+ or similar
```

### 2.3 Install Appium

```bash
npm install -g appium
```

### 2.4 Install the XCUITest Driver

```bash
appium driver install xcuitest
```

Verify Appium installation:
```bash
appium --version  # Should show 2.x
appium driver list --installed  # Should show xcuitest
```

---

## Step 3: Build and Install WebDriverAgent

This is the trickiest part with a free developer account.

### 3.1 Clone WebDriverAgent

```bash
cd ~
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

### 3.2 Open in Xcode

```bash
open WebDriverAgent.xcodeproj
```

### 3.3 Configure Signing (Free Account)

1. In Xcode, select **WebDriverAgentRunner** target (in the left sidebar, under WebDriverAgent project)

2. Go to **Signing & Capabilities** tab

3. Check **Automatically manage signing**

4. For **Team**, click the dropdown and select **Add an Account...**
   - Sign in with your Apple ID
   - Select your **Personal Team** (shows as "Your Name (Personal Team)")

5. **IMPORTANT**: Change the Bundle Identifier
   - Change from `com.facebook.WebDriverAgentRunner` to something unique
   - Example: `com.yourname.WebDriverAgentRunner`
   - Remember this - you'll need it for the config!

6. Repeat for **WebDriverAgentLib** target:
   - Select WebDriverAgentLib in the left sidebar
   - Same signing settings
   - Change bundle ID to `com.yourname.WebDriverAgentLib`

### 3.4 Connect Your iPhone

1. Connect your iPhone via USB cable
2. On iPhone: **Trust** the computer when prompted
3. In Xcode: Select your iPhone from the device dropdown (top of window)

### 3.5 Build WebDriverAgent

1. Select **WebDriverAgentRunner** target
2. Press **Cmd + B** to build
3. If you get signing errors:
   - Go to iPhone: **Settings → General → VPN & Device Management**
   - Find your developer profile and tap **Trust**
   - Build again in Xcode

### 3.6 Run WebDriverAgent Once

1. With WebDriverAgentRunner selected, press **Cmd + R** to run
2. Wait for it to install and launch on your iPhone
3. You should see a blank screen on the phone (this is normal)
4. In Xcode console, look for a URL like: `ServerURLHere->http://192.168.1.X:8100<-`
5. Stop the run (Cmd + .) - now WDA is installed on your device

> **Note**: With a free account, you'll need to rebuild every 7 days when the signing expires.

---

## Step 4: Configure the Automation

### 4.1 Find Your Device UDID

In Finder:
1. Connect your iPhone
2. Open **Finder** and select your iPhone in the sidebar
3. Click on the device info line (where it shows capacity) repeatedly
4. It will cycle through: Phone Number → UDID → ECID → Model
5. Copy the UDID

Or use Terminal:
```bash
# Install libimobiledevice for command-line tools
brew install libimobiledevice
idevice_id -l
```

### 4.2 Configure .env File

```bash
cd /path/to/auto-eatventure
cp .env-sample .env
```

Edit `.env` with your values:

```bash
# Set platform to iOS
PLATFORM="ios"

# Your device UDID from step 4.1
IOS_UDID="00008030-001234567890ABCD"

# Your iPhone name (as shown in Finder)
IOS_DEVICE_NAME="John's iPhone"

# Your iOS version
IOS_PLATFORM_VERSION="17.2"

# The bundle ID you set in Xcode (step 3.3)
WDA_BUNDLE_ID="com.yourname.WebDriverAgentRunner"

# Eatventure bundle ID (usually same as Android)
IOS_BUNDLE_ID="com.hwqgrhhjfd.idlefastfood"
```

### 4.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5: Capture iOS Template Images

Since the game UI has changed, you need to capture new template images.

### 5.1 Create iOS Templates Folder

```bash
mkdir -p matching_screenshots_ios/ads_crosses
```

### 5.2 Take Screenshots

1. Open Eatventure on your iPhone
2. Take screenshots at various game states (use iPhone screenshot: Side button + Volume Up)
3. Transfer screenshots to your Mac (AirDrop is fastest)

### 5.3 Crop Template Images

For each UI element, crop a small section that's unique and consistent:

| Template Name | What to Capture |
|---------------|-----------------|
| `notification.png` | The notification popup text/button |
| `settings.png` | The settings gear icon |
| `upgrade_button.png` | The upgrade button at bottom |
| `chest_icon.png` | The chest icon when available |
| `box.png` | A reward box floating in game |
| `investor.png` | The investor character |
| `buy_better_food_icon.png` | The food upgrade arrow icon |
| `go_next_level_icon.png` | Next level button/icon |
| `fly_next_city_icon.png` | Fly to new city button |
| `no_boost_indicator_2x.png` | The boost indicator when inactive |
| `offline_earnings.png` | Offline earnings popup |
| `first_lemonade_stand_open.png` | First stand open button |

Use Preview or any image editor to crop. Save as PNG files in `matching_screenshots_ios/`.

---

## Step 6: Calibrate Coordinates and Colors

### 6.1 Find Your Screen Resolution

Take a screenshot and check its dimensions:
```bash
# Check screenshot dimensions
file ~/Desktop/screenshot.png
# Example output: PNG image data, 1179 x 2556
```

Update `constants_ios.py`:
```python
IOS_WIDTH = 1179   # Your actual width
IOS_HEIGHT = 2556  # Your actual height
```

### 6.2 Fine-tune Button Coordinates

The coordinates are auto-scaled from Android, but you may need to adjust them:

1. Open a screenshot in Preview
2. Hover over UI elements to see pixel coordinates
3. Update specific coordinates in `constants_ios.py` if buttons aren't clicking correctly

### 6.3 Calibrate Color Detection (Important!)

The color detection values in `constants_ios.py` need updating for the new game version.

Use the Jupyter notebooks in `experiments/` folder:
1. `experiments/exp-use-investor/segmenting_investor.ipynb` - For investor colors
2. `experiments/exp-find-box/segmenting_box.ipynb` - For box colors

Or manually find HSV values:
```python
import cv2
import numpy as np

# Load your iOS screenshot
img = cv2.imread('screenshot.png')

# Click on the element you want to detect
# Note the BGR values, then convert to HSV
bgr_color = [180, 130, 45]  # Example
hsv = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)
print(f"HSV: {hsv[0][0]}")
```

Update the values in `constants_ios.py`:
```python
INVESTOR_COLORS_HSV = [
    (new_h1, new_s1, new_v1),
    (new_h2, new_s2, new_v2),
]
```

---

## Step 7: Run the Automation

### 7.1 Start Appium Server

In a Terminal window:
```bash
appium
```

Leave this running. You should see:
```
[Appium] Welcome to Appium v2.x.x
[Appium] Appium REST http interface listener started on http://0.0.0.0:4723
```

### 7.2 Run the Automation

In another Terminal:
```bash
cd /path/to/auto-eatventure
python autoplay_universal.py
```

The automation will:
1. Connect to your iPhone via Appium
2. Launch Eatventure
3. Start the automation loop

---

## Troubleshooting

### "Failed to connect to iOS device"

1. Check Appium is running: `appium` in separate terminal
2. Verify your device is connected: `idevice_id -l`
3. Check UDID in `.env` is correct
4. Make sure WebDriverAgent is installed (re-run from Xcode if needed)

### "WebDriverAgent not responding"

WebDriverAgent signing expired (7-day limit with free account):
1. Open Xcode
2. Select WebDriverAgentRunner
3. Press Cmd + B to rebuild
4. If prompted, trust the certificate again on iPhone

### "Template not found" warnings

You need to capture the iOS template images (Step 5).

### Buttons clicking wrong locations

1. Check your screen resolution in `constants_ios.py`
2. Take a screenshot and verify coordinates manually
3. Fine-tune specific coordinates that are off

### Colors not detecting (investors, boxes)

The game's color palette has changed. You need to recalibrate the HSV values (Step 6.3).

---

## Weekly Maintenance (Free Account)

Every 7 days, WebDriverAgent's signing expires. To fix:

1. Connect iPhone to Mac
2. Open Xcode
3. Open WebDriverAgent.xcodeproj
4. Select WebDriverAgentRunner target
5. Press Cmd + B to rebuild
6. Trust the certificate again on iPhone (Settings → General → VPN & Device Management)

---

## File Structure After Setup

```
auto-eatventure/
├── autoplay_universal.py    # Main script (run this!)
├── .env                      # Your configuration
├── constants_ios.py          # iOS coordinates and colors
├── ios_driver.py             # iOS device driver
├── matching_screenshots_ios/ # YOUR iOS template images
│   ├── notification.png
│   ├── settings.png
│   ├── upgrade_button.png
│   ├── chest_icon.png
│   ├── box.png
│   ├── investor.png
│   └── ...
└── ...
```

---

## Quick Reference Commands

```bash
# Start Appium server
appium

# Find device UDID
idevice_id -l

# Run automation
PLATFORM=ios python autoplay_universal.py

# Or if .env is configured:
python autoplay_universal.py

# Check Appium drivers
appium driver list --installed
```
