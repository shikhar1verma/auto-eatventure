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

# Area around the white settings gear: a dialog dims it, so it tells
# whether a dialog covers the screen (station popups don't dim it)
settings_roi_half_width_x = 30
settings_roi_half_height_y = 30

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

# Area of the red badge on the upgrade button (shown while an upgrade
# can be bought). The badge pulses, the area fits its largest size.
upgrade_badge_roi_left_x = 971
upgrade_badge_roi_right_x = 1107
upgrade_badge_roi_top_y = 2407
upgrade_badge_roi_bottom_y = 2542

# Area around the first row's buy button in the Upgrades dialog
# (centered on single_upgrade_button)
single_upgrade_roi_half_width_x = 100
single_upgrade_roi_half_height_y = 34

# Area around the red X (close) button of the Upgrades dialog
close_upgrade_roi_half_width_x = 40
close_upgrade_roi_half_height_y = 40

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

# Empty spot (restaurant just below the top bar) tapped to close
# station popups. y is only a fallback: the status bar height differs
# between phones, so at start the spot is placed below the top bar's
# black line (place_null_click_below_top_bar()). Too high, the top bar
# catches the tap and the popup stays open (OnePlus Nord 3); too low,
# it can hit a customer bubble, whose Investor dialog starts an ad
# with Claim (Xiaomi at y=340, 301 there).
null_click_x = 886
null_click_y = 278

chest_x = 110
chest_y = 734

close_chest_button_x = 1127
close_chest_button_y = 200

# ── Active Skills / Popular Dish ──────────────────────────────────────────────
# Black skill circle at the top center opens the Active Skills dialog.
# Single circle while all skills are ready (cooldown resets on every
# renovation / fly to a new city); it splits into two circles while
# Popular Dish is active or cooling down.

skills_circle_x = 610
skills_circle_y = 325

# Select / Start / Stop button of the Popular Dish row (same position)
popular_dish_button_x = 942
popular_dish_button_y = 1385

# Search area around the button: keeps the Sold Out row's own Select
# button (~305px lower) out of the match
popular_dish_button_roi_half_width_x = 175
popular_dish_button_roi_half_height_y = 90

# First (leftmost) tile in the "Select a dish" dialog. The grid has up
# to 3 tiles per row and is centered, so the first tile moves with the
# number of dishes: 3+ dishes / 2 dishes / 1 dish.
first_dish_3_tiles_x = 360
first_dish_2_tiles_x = 486
first_dish_1_tile_x = 610
first_dish_y = 1304

# ── Left button column ────────────────────────────────────────────────────────
# Taps on the left button column (helper, Food Delivery truck) use this
# x, right of the buttons' center (~75). Not side_button_zone_width_x,
# which keeps food taps away from the side buttons. On some phones (OnePlus Nord 3)
# the column is partly hidden behind the screen edge and taps on the
# buttons' left part (< ~90) are ignored.
side_button_tap_x = 120

# ── Food Delivery ─────────────────────────────────────────────────────────────
# Truck button in the left button column. It moves up when the button
# above it is missing, so it is searched in this area.
food_delivery_roi_left_x = 0
food_delivery_roi_right_x = 226
food_delivery_roi_top_y = 283
food_delivery_roi_bottom_y = 960

# Accept button of the first order in the "Food Delivery" dialog
food_delivery_accept_x = 610
food_delivery_accept_y = 1166
food_delivery_accept_roi_half_width_x = 147
food_delivery_accept_roi_half_height_y = 79

# ── Invite a Helper ───────────────────────────────────────────────────────────
# Helper (person) button, the top one in the left button column
helper_button_y = 434
# Search area of the "available" template (lower part of the button:
# person's body + the empty line where a countdown / ad icon would be)
helper_roi_left_x = 0
helper_roi_right_x = 170
helper_roi_top_y = 400
helper_roi_bottom_y = 560

# Invite button of the first helper in the "Invite a helper" dialog
helper_invite_x = 804
helper_invite_y = 1019
helper_invite_roi_half_width_x = 147
helper_invite_roi_half_height_y = 79

# ── Adventures ────────────────────────────────────────────────────────────────
# Party popper, the first white button in the right column; it opens
# the "Events" dialog with the Adventures at the bottom
events_button_x = 1141
events_button_y = 429

# Red X of the "Events" dialog and of an adventure's level dialog
# (e.g. "Feast on Olympus"); the red share around it tells which one
# is open
events_close_x = 1056
events_close_y = 797
adventure_level_close_x = 971
adventure_level_close_y = 734
dialog_close_roi_half_width_x = 34
dialog_close_roi_half_height_y = 34

# Swipe inside the "Events" dialog to its bottom (Adventures are last)
events_scroll_start_x = 610
events_scroll_start_y = 1717
events_scroll_end_x = 610
events_scroll_end_y = 859

# Search area of the adventures' key icons in the "Events" dialog;
# the Events section above them varies, so they are searched for
events_list_roi_left_x = 68
events_list_roi_right_x = 1152
events_list_roi_top_y = 791
events_list_roi_bottom_y = 2181
# An adventure's Enter button relative to the center of its key icon
adventure_enter_offset_x = 70
adventure_enter_offset_y = 118

# Level dialog: right arrow (shown when the last level is not
# selected), keys counter icon (key or ad) and "Complete last level"
adventure_right_arrow_x = 898
adventure_right_arrow_y = 1045
adventure_right_arrow_roi_half_width_x = 73
adventure_right_arrow_roi_half_height_y = 96
adventure_counter_roi_left_x = 474
adventure_counter_roi_right_x = 723
adventure_counter_roi_top_y = 1751
adventure_counter_roi_bottom_y = 1876
adventure_complete_last_x = 412
adventure_complete_last_y = 1949

# Full screen reward cards: taps reveal them one by one, then the
# summary shows a red X in the top right corner. An empty area of the
# screen's dark blue background tells the reward screen.
adventure_reward_bg_roi_left_x = 0
adventure_reward_bg_roi_right_x = 181
adventure_reward_bg_roi_top_y = 395
adventure_reward_bg_roi_bottom_y = 621
adventure_reveal_tap_x = 610
adventure_reveal_tap_y = 1356
adventure_summary_close_x = 1118
adventure_summary_close_y = 186
adventure_summary_close_roi_half_width_x = 56
adventure_summary_close_roi_half_height_y = 56

# ── Station upgrade icons ─────────────────────────────────────────────────────
# Height range of the white arrow in the pulsing red upgrade icon
# (measured 26-41 on Xiaomi, 27-35 on OnePlus Nord 3)
upgrade_arrow_min_height_y = 22
upgrade_arrow_max_height_y = 48

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
