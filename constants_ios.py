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
# iPhone 14 Pro: 393 x 852 points (1179 x 2556 pixels at 3x scale)
# Appium uses POINTS, not pixels!
IOS_WIDTH = 393   # Points
IOS_HEIGHT = 852  # Points

# ============================================================
# UI ELEMENT COORDINATES (in points, not pixels!)
# Based on iPhone 14 Pro (393 x 852 points)
# Calibrate these by taking screenshots and checking coordinates
# ============================================================

close_nofication_coords = {
    'x': 196,
    'y': 520
}

first_lemonade_stand_open_coords = {
    'x': 196,
    'y': 510
}

settings_coords = {
    'x': 370,
    'y': 35
}

cloud_save_coords = {
    'x': 196,
    'y': 450
}

email_input_coords = {
    'x': 196,
    'y': 360
}

password_input_coords = {
    'x': 196,
    'y': 440
}

text_ok_button_coords = {
    'x': 370,
    'y': 510
}

login_button_coords = {
    'x': 196,
    'y': 530
}

use_cloud_save_button_coords = {
    'x': 270,
    'y': 575
}

close_game_for_restart_button_coords = {
    'x': 196,
    'y': 500
}

close_offline_earnings_coords = {
    'x': 315,
    'y': 320
}

# Bottom right blue up-arrow button
upgrade_button_coords = {
    'x': 355,
    'y': 815
}

single_upgrade_button_coords = {
    'x': 310,
    'y': 350
}

close_upgrade_button_coords = {
    'x': 335,
    'y': 285
}

next_level_button_coords = {
    'x': 40,
    'y': 815
}

renovate_button_coords = {
    'x': 196,
    'y': 600
}

ads_button_coords = {
    'x': 196,
    'y': 820
}

fly_next_city_button_coords = {
    'x': 196,
    'y': 560
}

welcome_city_ok_button_coords = {
    'x': 200,
    'y': 535
}

null_click_coords = {
    'x': 220,
    'y': 90
}

chest_coords = {
    'x': 35,
    'y': 230
}

close_chest_button_coords = {
    'x': 365,
    'y': 60
}

# ============================================================
# SWIPE COORDINATES (in points)
# ============================================================

swipe_layout_down_coords = {
    'start': {
        'x': 196,
        'y': 680
    },
    'end': {
        'x': 196,
        'y': 220
    }
}

swipe_layout_up_coords = {
    'end': {
        'x': 196,
        'y': 680
    },
    'start': {
        'x': 196,
        'y': 220
    }
}

swipe_layout_little_up_coords = {
    'end': {
        'x': 196,
        'y': 410
    },
    'start': {
        'x': 196,
        'y': 220
    }
}

swipe_layout_little_down_coords = {
    'start': {
        'x': 196,
        'y': 410
    },
    'end': {
        'x': 196,
        'y': 220
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
# Original Android values - UPDATE THESE
INVESTOR_COLORS_HSV = [
    (26, 80, 105),
    (25, 94, 119),
    (26, 108, 139),
    (26, 110, 135)
]
INVESTOR_COLOR_TOLERANCE = 15

# Box detection colors (HSV format)
# Original Android values - UPDATE THESE
BOX_COLORS_HSV = [
    (13, 152, 171),
    (14, 155, 140)
]
BOX_COLOR_TOLERANCE = 2

# Boost indicator yellow color (BGR format)
# Used to detect if boost is active
BOOST_INDICATOR_COLOR_BGR = [42, 192, 255]

# Boost indicator check line coordinates (in points)
BOOST_CHECK_START = {'x': 110, 'y': 75}
BOOST_CHECK_END = {'x': 125, 'y': 75}

# ============================================================
# DANGER ZONES (in points)
# Y coordinates that are too close to edges/menus
# ============================================================

# Maximum Y coordinate for safe food item detection
DANGER_Y_MAX = 735

# Minimum Y coordinate (items too high can overlap with UI)
DANGER_Y_MIN = 300

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
