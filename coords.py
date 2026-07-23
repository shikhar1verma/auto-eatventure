# coords.py
# All resolution-dependent pixel values for a specific device.
# When adding support for new devices, create a profile that overrides these values.

# ── Reference Resolution ──────────────────────────────────────────────────────
# All coordinates below are calibrated for this resolution.
# ScaledCoords uses these to proportionally scale to the actual device resolution.

REFERENCE_WIDTH = 1220
REFERENCE_HEIGHT = 2712

# ── UI Button Tap Coordinates ─────────────────────────────────────────────────

close_notification_x = 602
close_notification_y = 1646

first_lemonade_stand_open_x = 604
first_lemonade_stand_open_y = 1604

settings_x = 1134
settings_y = 161

cloud_save_x = 554
cloud_save_y = 1419

email_input_x = 593
email_input_y = 1147

password_input_x = 593
password_input_y = 1391

text_ok_button_x = 1164
text_ok_button_y = 1604

login_button_x = 593
login_button_y = 1686

use_cloud_save_button_x = 839
use_cloud_save_button_y = 1825

close_game_for_restart_x = 622
close_game_for_restart_y = 1583

close_offline_earnings_x = 974
close_offline_earnings_y = 1012

upgrade_button_x = 1093
upgrade_button_y = 2524

single_upgrade_button_x = 968
single_upgrade_button_y = 1115

close_upgrade_button_x = 1035
close_upgrade_button_y = 908

next_level_button_x = 127
next_level_button_y = 2521

renovate_button_x = 593
renovate_button_y = 1912

ads_button_x = 610
ads_button_y = 2564

fly_next_city_button_x = 593
fly_next_city_button_y = 1892

welcome_city_ok_button_x = 618
welcome_city_ok_button_y = 1695

null_click_x = 686
null_click_y = 278

chest_x = 110
chest_y = 734

close_chest_button_x = 1127
close_chest_button_y = 200

# ── Swipe Coordinates ─────────────────────────────────────────────────────────
# Distance kept to 650px: the usable playfield height (excluding side
# buttons/ad banner zones) is only ~820px, so a swipe close to that
# length would risk jumping straight over a row of stations. 650px
# leaves ~170px (~20%) overlap between consecutive swipes.

swipe_layout_down_start_x = 646
swipe_layout_down_start_y = 1889
swipe_layout_down_end_x = 646
swipe_layout_down_end_y = 1239

swipe_layout_up_start_x = 646
swipe_layout_up_start_y = 604
swipe_layout_up_end_x = 646
swipe_layout_up_end_y = 1254

swipe_layout_little_up_start_x = 646
swipe_layout_little_up_start_y = 604
swipe_layout_little_up_end_x = 646
swipe_layout_little_up_end_y = 1133

swipe_layout_little_down_start_x = 646
swipe_layout_little_down_start_y = 1133
swipe_layout_little_down_end_x = 646
swipe_layout_little_down_end_y = 604

# ── Y-Boundary Thresholds ─────────────────────────────────────────────────────

# Items below this Y are excluded from food icon detection (avoids club icon area)
danger_max_y = 2200

# Food icons below this Y AND within the left side button zone are excluded
# (their station box may overlap the club button in the bottom-left corner)
club_button_danger_min_y = 2029

# Food icons above this Y need special click offset to avoid tooltip overlap
food_icon_tooltip_boundary_y = 1240

# ── Investor & Ad Button Coordinates (adb_autoplay) ───────────────────────────

redeem_investor_reward_x = 720
redeem_investor_reward_y = 2020

ad_button_x = 720
ad_button_y = 2950

# ── Boost Detection Pixel Positions ───────────────────────────────────────────
# Pixel range checked for yellow color to detect if 2x boost is active

boost_check_pixel1_x = 408
boost_check_pixel1_y = 274

boost_check_pixel2_x = 466
boost_check_pixel2_y = 274

# ── Click Offsets ─────────────────────────────────────────────────────────────

# Y offset when tapping a food icon to open its upgrade menu
upgrade_food_offset_y = 22

# Small shift applied to the food icon tap to avoid misclicking an
# adjacent station when two stations are close together
upgrade_click_shift_x = 2
upgrade_click_shift_y = 2

# Offsets for the click-and-hold gesture that opens the "buy better food" menu
better_food_neg_offset_y = 130
better_food_pos_offset_x = 20

# X offset for clicking the "buy better food" button relative to the food icon
better_food_neg_offset_x = 110

# Width of the side UI buttons (restaurant race, food boxes, etc.)
# pinned to the left/right screen edges. Clicks are kept at least
# this far from either edge to avoid triggering them.
side_button_zone_width_x = 180

# Offset applied when clicking a detected small investor icon
small_investor_click_offset_x = 10
small_investor_click_offset_y = 10

# Offset applied when clicking a detected large investor icon
large_investor_click_offset_x = 55
large_investor_click_offset_y = 100

# ── DBSCAN Clustering ─────────────────────────────────────────────────────────

# Max pixel distance between points to be considered in the same cluster
dbscan_eps = 10

# ── Initial Tap Coordinates (autoplay.py / Appium) ────────────────────────────

initial_tap_x = 709
initial_tap_y = 1851

# Y position above which a food icon is considered too close to the top of the viewport,
# triggering a swipe-up to reposition the layout
food_icon_top_boundary_y = 1100

# Radius of the circle drawn around matched template locations
annotation_radius = 14
