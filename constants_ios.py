"""
iOS-specific coordinates and constants for Eatventure automation.

IMPORTANT: These coordinates are TEMPLATES based on iPhone 14 Pro (1179x2556).
You MUST calibrate these for your specific device by:
1. Taking screenshots of the game
2. Finding the exact pixel coordinates of each UI element
3. Updating the values below

The Android version uses a 1440x3120 screen (Pixel 6 Pro).
iOS coordinates are scaled proportionally but may need fine-tuning.

To find coordinates on your device:
1. Take a screenshot: Use Xcode or the screenshot tool
2. Open in Preview/Photoshop
3. Hover over UI elements to see pixel coordinates
"""

# Screen dimensions for reference
# iPhone 14 Pro: 1179 x 2556 pixels (393 x 852 points at 3x scale)
# All coordinates below are in PIXELS (driver auto-converts to points)
IOS_WIDTH = 1179   # Pixels
IOS_HEIGHT = 2556  # Pixels

# ============================================================
# UI ELEMENT COORDINATES (in pixels - auto-converted to points by driver)
# Based on iPhone 14 Pro (1179 x 2556 pixels)
# Calibrate by checking screenshot pixel coordinates
# ============================================================

close_nofication_coords = {
    'x': 590,
    'y': 1560
}

first_lemonade_stand_open_coords = {
    'x': 590,
    'y': 1530
}

settings_coords = {
    'x': 1110,
    'y': 105
}

cloud_save_coords = {
    'x': 590,
    'y': 1350
}

email_input_coords = {
    'x': 590,
    'y': 1080
}

password_input_coords = {
    'x': 590,
    'y': 1320
}

text_ok_button_coords = {
    'x': 1110,
    'y': 1530
}

login_button_coords = {
    'x': 590,
    'y': 1590
}

use_cloud_save_button_coords = {
    'x': 810,
    'y': 1725
}

close_game_for_restart_button_coords = {
    'x': 590,
    'y': 1500
}

close_offline_earnings_coords = {
    'x': 945,
    'y': 960
}

# Bottom right blue up-arrow button
# Moved up slightly to avoid iOS safe area at bottom
upgrade_button_coords = {
    'x': 1070,
    'y': 2380
}

single_upgrade_button_coords = {
    'x': 930,
    'y': 1050
}

close_upgrade_button_coords = {
    'x': 1005,
    'y': 855
}

next_level_button_coords = {
    'x': 120,
    'y': 2380
}

renovate_button_coords = {
    'x': 590,
    'y': 1800
}

ads_button_coords = {
    'x': 590,
    'y': 2380
}

fly_next_city_button_coords = {
    'x': 590,
    'y': 1680
}

welcome_city_ok_button_coords = {
    'x': 600,
    'y': 1605
}

null_click_coords = {
    'x': 660,
    'y': 270
}

chest_coords = {
    'x': 105,
    'y': 690
}

close_chest_button_coords = {
    'x': 1095,
    'y': 180
}

# ============================================================
# SWIPE COORDINATES (in pixels)
# ============================================================

swipe_layout_down_coords = {
    'start': {
        'x': 590,
        'y': 2040
    },
    'end': {
        'x': 590,
        'y': 660
    }
}

swipe_layout_up_coords = {
    'end': {
        'x': 590,
        'y': 2040
    },
    'start': {
        'x': 590,
        'y': 660
    }
}

swipe_layout_little_up_coords = {
    'end': {
        'x': 590,
        'y': 1230
    },
    'start': {
        'x': 590,
        'y': 660
    }
}

swipe_layout_little_down_coords = {
    'start': {
        'x': 590,
        'y': 1230
    },
    'end': {
        'x': 590,
        'y': 660
    }
}

# ============================================================
# COLOR DETECTION VALUES (HSV)
# IMPORTANT: These MUST be recalibrated for iOS/new game version
#
# To calibrate:
# 1. Take iOS screenshots of the game
# 2. Use the Jupyter notebooks in experiments/ folder
# 3. Update the HSV values below
# ============================================================

# Investor detection colors (HSV format)
# Calibrated for iOS - skin tones of character
INVESTOR_COLORS_HSV = [
    (15, 120, 200),   # Light skin tone
    (18, 100, 220),
    (20, 90, 200),
    (22, 110, 210)
]
INVESTOR_COLOR_TOLERANCE = 20

# Box detection colors (HSV format)
# Calibrated for iOS - cardboard brown
BOX_COLORS_HSV = [
    (15, 140, 180),
    (18, 150, 160),
    (12, 130, 170)
]
BOX_COLOR_TOLERANCE = 10

# Boost indicator yellow color (BGR format)
# Used to detect if boost is active
BOOST_INDICATOR_COLOR_BGR = [42, 192, 255]

# Boost indicator check line coordinates (in pixels)
BOOST_CHECK_START = {'x': 330, 'y': 225}
BOOST_CHECK_END = {'x': 375, 'y': 225}

# ============================================================
# DANGER ZONES (in pixels)
# Y coordinates that are too close to edges/menus
# ============================================================

# Maximum Y coordinate for safe food item detection
# Set lower to exclude bottom bar buttons (upgrade button at ~2445)
DANGER_Y_MAX = 2150

# Minimum Y coordinate (items too high can overlap with UI)
# Lowered to allow chest detection at y~690-840
DANGER_Y_MIN = 600

# ============================================================
# TIMING CONSTANTS
# iOS may need different timings than Android
# ============================================================

# Time to wait after clicking (seconds)
CLICK_DELAY = 0.2

# Time to wait for app to launch (seconds)
APP_LAUNCH_DELAY = 2.0

# Time to wait for game state changes (seconds)
STATE_CHANGE_DELAY = 1.0

# Long press duration (milliseconds)
LONG_PRESS_DURATION = 1200
