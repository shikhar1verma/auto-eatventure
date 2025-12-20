"""
PlayCover-specific coordinates and constants for Eatventure automation.

PlayCover runs iOS apps on Apple Silicon Macs in a window.
The window size depends on your PlayCover settings.

IMPORTANT: These coordinates are based on a window matching iPhone aspect ratio.
You may need to calibrate them for your specific window size.

To calibrate:
1. Take a screenshot of the game in PlayCover
2. Open the screenshot and find pixel coordinates of UI elements
3. Update the values below

Recommended PlayCover settings:
- Set window to a fixed size (e.g., 393x852 to match iPhone 14 Pro points)
- Or use a larger size like 590x1278 (1.5x scale)
"""

# Window dimensions for reference
# These should match your PlayCover window size
# Default: iPhone 14 Pro points (393 x 852)
PLAYCOVER_WIDTH = 393
PLAYCOVER_HEIGHT = 852

# Scale factor if using a different window size
# Set to 1.0 if using 393x852, or calculate for your size
# Example: If window is 590x1278, scale = 590/393 = 1.5
COORDINATE_SCALE = 1.0

# ============================================================
# UI ELEMENT COORDINATES (in window pixels)
# Based on iPhone 14 Pro point coordinates (393 x 852)
# If using a different window size, these will be auto-scaled
# ============================================================

close_nofication_coords = {
    'x': 197,
    'y': 520
}

first_lemonade_stand_open_coords = {
    'x': 197,
    'y': 510
}

settings_coords = {
    'x': 370,
    'y': 35
}

cloud_save_coords = {
    'x': 197,
    'y': 450
}

email_input_coords = {
    'x': 197,
    'y': 360
}

password_input_coords = {
    'x': 197,
    'y': 440
}

text_ok_button_coords = {
    'x': 370,
    'y': 510
}

login_button_coords = {
    'x': 197,
    'y': 530
}

use_cloud_save_button_coords = {
    'x': 270,
    'y': 575
}

close_game_for_restart_button_coords = {
    'x': 197,
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
    'x': 197,
    'y': 600
}

ads_button_coords = {
    'x': 197,
    'y': 820
}

fly_next_city_button_coords = {
    'x': 197,
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
# SWIPE COORDINATES
# ============================================================

swipe_layout_down_coords = {
    'start': {
        'x': 197,
        'y': 680
    },
    'end': {
        'x': 197,
        'y': 220
    }
}

swipe_layout_up_coords = {
    'end': {
        'x': 197,
        'y': 680
    },
    'start': {
        'x': 197,
        'y': 220
    }
}

swipe_layout_little_up_coords = {
    'end': {
        'x': 197,
        'y': 410
    },
    'start': {
        'x': 197,
        'y': 220
    }
}

swipe_layout_little_down_coords = {
    'start': {
        'x': 197,
        'y': 410
    },
    'end': {
        'x': 197,
        'y': 220
    }
}

# ============================================================
# COLOR DETECTION VALUES (HSV)
# Same as iOS since it's the same app
# ============================================================

# Investor detection colors (HSV format)
INVESTOR_COLORS_HSV = [
    (15, 120, 200),
    (18, 100, 220),
    (20, 90, 200),
    (22, 110, 210)
]
INVESTOR_COLOR_TOLERANCE = 20

# Box detection colors (HSV format)
BOX_COLORS_HSV = [
    (15, 140, 180),
    (18, 150, 160),
    (12, 130, 170)
]
BOX_COLOR_TOLERANCE = 10

# Boost indicator yellow color (BGR format)
BOOST_INDICATOR_COLOR_BGR = [42, 192, 255]

# Boost indicator check line coordinates
BOOST_CHECK_START = {'x': 110, 'y': 75}
BOOST_CHECK_END = {'x': 125, 'y': 75}

# ============================================================
# DANGER ZONES
# Y coordinates that are too close to edges/menus
# ============================================================

# Maximum Y coordinate for safe food item detection
DANGER_Y_MAX = 715

# Minimum Y coordinate
DANGER_Y_MIN = 200

# ============================================================
# TIMING CONSTANTS
# ============================================================

CLICK_DELAY = 0.2
APP_LAUNCH_DELAY = 2.0
STATE_CHANGE_DELAY = 1.0
LONG_PRESS_DURATION = 1200
