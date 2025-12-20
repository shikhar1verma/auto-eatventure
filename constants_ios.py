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
# Android (Pixel 6 Pro): 1440 x 3120
# iPhone 14 Pro: 1179 x 2556
# Scale factor: ~0.82 (width) and ~0.82 (height)

# Scaling helper (adjust base dimensions for your device)
ANDROID_WIDTH = 1440
ANDROID_HEIGHT = 3120
IOS_WIDTH = 1179  # Update for your iPhone model
IOS_HEIGHT = 2556  # Update for your iPhone model

def scale_x(android_x):
    """Scale X coordinate from Android to iOS."""
    return int(android_x * IOS_WIDTH / ANDROID_WIDTH)

def scale_y(android_y):
    """Scale Y coordinate from Android to iOS."""
    return int(android_y * IOS_HEIGHT / ANDROID_HEIGHT)

def scale_coords(android_coords):
    """Scale coordinate dict from Android to iOS."""
    return {
        'x': scale_x(android_coords['x']),
        'y': scale_y(android_coords['y'])
    }

# ============================================================
# UI ELEMENT COORDINATES
# These are scaled from Android - CALIBRATE FOR YOUR DEVICE
# ============================================================

close_nofication_coords = {
    'x': scale_x(710),
    'y': scale_y(1894)
}

first_lemonade_stand_open_coords = {
    'x': scale_x(713),
    'y': scale_y(1845)
}

settings_coords = {
    'x': scale_x(1339),
    'y': scale_y(185)
}

cloud_save_coords = {
    'x': scale_x(654),
    'y': scale_y(1632)
}

email_input_coords = {
    'x': scale_x(700),
    'y': scale_y(1320)
}

password_input_coords = {
    'x': scale_x(700),
    'y': scale_y(1600),
}

text_ok_button_coords = {
    'x': scale_x(1374),
    'y': scale_y(1845),
}

login_button_coords = {
    'x': scale_x(700),
    'y': scale_y(1940)
}

use_cloud_save_button_coords = {
    'x': scale_x(990),
    'y': scale_y(2100)
}

close_game_for_restart_button_coords = {
    'x': scale_x(734),
    'y': scale_y(1821)
}

close_offline_earnings_coords = {
    'x': scale_x(1150),
    'y': scale_y(1164)
}

upgrade_button_coords = {
    'x': scale_x(1290),
    'y': scale_y(2904)
}

single_upgrade_button_coords = {
    'x': scale_x(1143),
    'y': scale_y(1283)
}

close_upgrade_button_coords = {
    'x': scale_x(1222),
    'y': scale_y(1045)
}

next_level_button_coords = {
    'x': scale_x(150),
    'y': scale_y(2900)
}

renovate_button_coords = {
    'x': scale_x(700),
    'y': scale_y(2200)
}

ads_button_coords = {
    'x': scale_x(720),
    'y': scale_y(2950)
}

fly_next_city_button_coords = {
    'x': scale_x(700),
    'y': scale_y(2050)
}

welcome_city_ok_button_coords = {
    'x': scale_x(730),
    'y': scale_y(1950)
}

null_click_coords = {
    'x': scale_x(810),
    'y': scale_y(320)
}

chest_coords = {
    'x': scale_x(130),
    'y': scale_y(845)
}

close_chest_button_coords = {
    'x': scale_x(1330),
    'y': scale_y(230)
}

# ============================================================
# SWIPE COORDINATES
# ============================================================

swipe_layout_down_coords = {
    'start': {
        'x': scale_x(900),
        'y': scale_y(2500)
    },
    'end': {
        'x': scale_x(900),
        'y': scale_y(800)
    }
}

swipe_layout_up_coords = {
    'end': {
        'x': scale_x(900),
        'y': scale_y(2500)
    },
    'start': {
        'x': scale_x(900),
        'y': scale_y(800)
    }
}

swipe_layout_little_up_coords = {
    'end': {
        'x': scale_x(900),
        'y': scale_y(1500)
    },
    'start': {
        'x': scale_x(900),
        'y': scale_y(800)
    }
}

swipe_layout_little_down_coords = {
    'start': {
        'x': scale_x(900),
        'y': scale_y(1500)
    },
    'end': {
        'x': scale_x(900),
        'y': scale_y(800)
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

# Boost indicator check line coordinates
BOOST_CHECK_START = {'x': scale_x(408), 'y': scale_y(274)}
BOOST_CHECK_END = {'x': scale_x(466), 'y': scale_y(274)}

# ============================================================
# DANGER ZONES
# Y coordinates that are too close to edges/menus
# ============================================================

# Maximum Y coordinate for safe food item detection
DANGER_Y_MAX = scale_y(2690)

# Minimum Y coordinate (items too high can overlap with UI)
DANGER_Y_MIN = scale_y(1100)

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
