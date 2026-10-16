"""
game_actions.py - High-level game action methods

Each method represents a complete game action that can be
called from the main loop. Methods are self-contained and
handle their own screenshot refreshes when needed.
"""

import time
import random

from logger import get_logger, get_key_logger

log = get_logger(__name__)
key_log = get_key_logger()


# Number of consecutive swipes in the same direction before reversing.
# Kept high enough that repeats * swipe distance (650px) still covers
# the same total travel as the old single 1285px swipe used to, so a
# full stale-swipe cycle still reaches the top/bottom of a tall level.
SWIPES_PER_DIRECTION = 7
STALE_RECOVERY_THRESHOLD = 50
STALE_SWIPE_THRESHOLD = 15

# The "Welcome to <city>" dialog (Okay) appears after the flight
# animation (~15-19 s) and the "Open" dialog of the first stand after
# the renovate animation / Okay; both are slow on some phones. They
# are awaited up to this long; then tapped blindly (e.g. closed by
# hand).
WELCOME_OKAY_TIMEOUT_S = 60
OPEN_BUTTON_TIMEOUT_S = 45
# Delay before tapping, so the dialog finishes its pop-in animation
DIALOG_BUTTON_TAP_DELAY_S = 1

# Time for the Active Skills / Select a dish dialogs to animate
SKILL_DIALOG_DELAY_S = 1.5

# Time for the Food Delivery dialog to open / close
FOOD_DELIVERY_DIALOG_DELAY_S = 1.5

# The "Invite a helper" dialog shows "Loading..." for a few seconds
# before the helper list appears; it is awaited up to this long
HELPER_DIALOG_TIMEOUT_S = 10
# Time for the "Invite a helper" dialog to close after Invite
HELPER_DIALOG_DELAY_S = 1.5
# Max SQDIFF of the "available" helper button. Lower than the default:
# the black person with only an ad icon under it scores ~0.03.
HELPER_AVAILABLE_MAX_DIFF = 0.015

# Red badge on the upgrade button = an upgrade can be bought. It
# pulses (size, tilt), which made template matching miss ~1/3 of the
# frames, so its red pixels are counted (red wraps around hue 180).
# The badge covers ~21-30% of its area, 0% when it is not shown; red
# food in customers' bubbles behind the area reached ~5%.
UPGRADE_BADGE_RED = [((0, 120, 150), (8, 255, 255)),
                     ((172, 120, 150), (180, 255, 255))]
UPGRADE_BADGE_MIN_RATIO = 0.12
# Buy button of the first row in the Upgrades dialog: blue while
# affordable, grey when not (bought upgrades leave the list, so the
# next one moves to the first row)
UPGRADE_BUY_BLUE = [((95, 120, 200), (110, 255, 255))]
UPGRADE_BUY_MIN_RATIO = 0.3
# Upgrades are bought in rounds of this many taps, each preceded by a
# check of the first row, up to UPGRADE_MAX_CLICKS (a new level)
UPGRADE_CLICKS_PER_CHECK = 5
UPGRADE_MAX_CLICKS = 50
# Time for the Upgrades dialog to pop in before the first check
UPGRADE_DIALOG_OPEN_DELAY_S = 0.5
# Time for a station popup to close after a tap on the null spot
STATION_POPUP_CLOSE_DELAY_S = 0.3
# The red X of the open dialog fills ~80% of its area (same red as the
# badge), ~0-10% without the dialog
UPGRADES_DIALOG_MIN_RATIO = 0.4
# The closed Upgrades dialog fades out for ~0.6 s; a screenshot taken
# meanwhile hides the food icons (with the badge still shown, the next
# loops kept missing the stations and went stale)
UPGRADE_DIALOG_CLOSE_DELAY_S = 0.8

# The white settings gear (top right) has max brightness 255 on the
# restaurant, 2-11 under a dialog and 160-236 while a dialog animates.
# Station popups don't dim it.
SETTINGS_GEAR_MIN_BRIGHTNESS = 200
# Dialogs closed at start before the null spot is placed, at most
DIMMING_DIALOG_CLOSE_TRIES = 5
# Start dialogs ("While you were away...", Offline Earnings) come
# when the server answers, up to ~30 s after the game is ready, and
# not on every start. The screen is watched this long after the start.
START_DIALOGS_WATCH_S = 30
START_DIALOGS_CHECK_S = 2
# Red X popups closed at most when the game is stale (stacked dialogs)
STALE_POPUP_CLOSE_TRIES = 3
# "Restaurant Race ended!" (no X, only Claim): title / Claim templates
# score 0.96-1.00, <= 0.57 on all other screens
RACE_TEMPLATE_THRESHOLD = 0.8
RACE_CLAIM_DELAY_S = 1.5
# The templates match a dimmed dialog too; Claim is tapped only when
# its button is bright (mean V ~240), i.e. no other dialog covers it
RACE_CLAIM_MIN_BRIGHTNESS = 200
# The top bar ends with a black line across the screen (Xiaomi y=226,
# OnePlus Nord 3 y=284; the status bar height differs). Black row =
# over 90 % of its pixels have every channel below 10. Searched in
# this band of the screen height: ads and loading screens have black
# rows higher up.
TOP_BAR_LINE_MAX_VALUE = 10
TOP_BAR_LINE_MIN_RATIO = 0.9
TOP_BAR_BAND_TOP = 0.06
TOP_BAR_BAND_BOTTOM = 0.15
# Shorter runs of black rows (reference px) are gaps between HUD
# elements, not the line (Xiaomi: 13 rows; one row under two dialogs)
TOP_BAR_LINE_MIN_ROWS_Y = 5
# The null spot is this far (reference px) below the line: still on
# the restaurant (the top bar catches taps, popups stay open) but
# above the tables, whose customer bubbles open dialogs (Investor's
# Claim starts an ad)
NULL_CLICK_BELOW_TOP_BAR_Y = 22

# Adventures: (name, key icon in the "Events" list, key icon in the
# level dialog). The counter shows a key while free runs are left and
# an ad icon (never tapped) when the keys are used up. Key templates
# score 0.93-1.00, the other adventure's key and the ad icon <= 0.46.
ADVENTURES = [
  ("Zeus' Feast", 'adventure_zeus_key', 'adventure_zeus_dialog_key'),
  ('Hangry Pirates', 'adventure_pirates_key',
   'adventure_pirates_dialog_key'),
]
ADVENTURE_KEY_THRESHOLD = 0.8
# The red X of an open dialog fills ~75% of its area, <= 13% when the
# dialog is closed or covered; the reward summary's X ~89%, 0% before
ADVENTURE_CLOSE_RED_MIN_RATIO = 0.5
# Right arrow of the level dialog ~46% blue, 0% on the last level. The
# Events dialog has blue Enter buttons there, so it is checked only
# with the level dialog open.
ADVENTURE_ARROW_BLUE = [((95, 120, 150), (115, 255, 255))]
ADVENTURE_ARROW_MIN_RATIO = 0.2
# Background of the full screen reward cards, dark blue for Zeus'
# Feast, brown for Hangry Pirates: 100% in its empty area, <= 7% on
# the restaurant and the dialogs
ADVENTURE_REWARD_BG = [((95, 200, 110), (105, 255, 150)),
                       ((16, 130, 140), (26, 185, 195))]
ADVENTURE_REWARD_BG_MIN_RATIO = 0.8
# Time for the dialogs and reward screens to open / close
ADVENTURE_DIALOG_DELAY_S = 1.5
ADVENTURE_REVEAL_DELAY_S = 1.5
# The reward screen after "Complete last level" is awaited up to this
# long
ADVENTURE_REWARD_TIMEOUT_S = 10
# Safety limits: arrow taps to the last level, taps to reveal one
# run's cards (1 to ~10, one more shows the summary) and runs per
# adventure (bonus key cards add runs)
ADVENTURE_MAX_ARROW_TAPS = 30
ADVENTURE_MAX_REVEAL_TAPS = 15
ADVENTURE_MAX_RUNS = 10

POPULAR_DISH_BUTTON_TEMPLATES = {
  'select': 'popular_dish_select',
  'start': 'popular_dish_start',
  'stop': 'popular_dish_stop',
}


class GameActions:
  """Game action methods that operate on a Device and
  TemplateMatcher."""

  def __init__(self, device, matcher, loc):
    self.device = device
    self.matcher = matcher
    self.loc = loc
    self.sc = device.sc

  # ── Detection helpers ─────────────────────────────────────

  def _hsv(self):
    return self.device.current_cv2_sc_bgr2hsv

  def _gray(self):
    return self.device.current_cv2_sc_grayscale

  def _bgr(self):
    return self.device.current_cv2_sc

  def is_having_notification(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'notification')

  def is_having_first_lemonade_stand_open(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'first_lemondae_stand_open')

  def is_having_settings(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'settings')

  def is_having_offline_earnings(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'offline_earnings')

  def is_having_upgrade(self):
    """Red badge on the upgrade button."""
    roi = self._hsv()[
      self.sc.upgrade_badge_roi_top_y:self.sc.upgrade_badge_roi_bottom_y,
      self.sc.upgrade_badge_roi_left_x:self.sc.upgrade_badge_roi_right_x]
    return (self.matcher.color_ratio(roi, UPGRADE_BADGE_RED)
            >= UPGRADE_BADGE_MIN_RATIO)

  def is_having_upgrades_dialog(self):
    """Red X (close) button of the Upgrades dialog."""
    x = self.sc.close_upgrade_button_x
    y = self.sc.close_upgrade_button_y
    hw = self.sc.close_upgrade_roi_half_width_x
    hh = self.sc.close_upgrade_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    return (self.matcher.color_ratio(roi, UPGRADE_BADGE_RED)
            >= UPGRADES_DIALOG_MIN_RATIO)

  def is_first_upgrade_affordable(self):
    """Blue buy button of the first row in the Upgrades dialog."""
    x = self.sc.single_upgrade_button_x
    y = self.sc.single_upgrade_button_y
    hw = self.sc.single_upgrade_roi_half_width_x
    hh = self.sc.single_upgrade_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    return (self.matcher.color_ratio(roi, UPGRADE_BUY_BLUE)
            >= UPGRADE_BUY_MIN_RATIO)

  def is_having_open_button(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'open_button', threshold=0.9)

  def is_having_welcome_city_okay(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'welcome_city_okay', threshold=0.9)

  def is_having_next_level_icon(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'go_next_level', threshold=0.95)

  def is_having_fly_next_city_icon(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'fly_next_city_icon', threshold=0.95)

  def is_having_chest_icon(self):
    return self.matcher.is_hsv_match(
      self._hsv(), 'chest_icon')

  def is_having_no_boost_indicator(self):
    start = {
      'x': self.sc.boost_check_pixel1_x,
      'y': self.sc.boost_check_pixel1_y}
    end = {
      'x': self.sc.boost_check_pixel2_x,
      'y': self.sc.boost_check_pixel2_y}
    color_to_check = [42, 192, 255]
    return not self.matcher.is_pixel_color_between(
      self._bgr(), start, end, color_to_check)

  def is_having_small_investor_icon(self):
    return self.matcher.is_grayscale_match(
      self._gray(), 'small_investor_icon')

  def is_having_investor(self):
    sc = self.matcher.apply_investor_mask(self._bgr())
    template = self.matcher.apply_investor_mask(
      self.matcher.templates['investor']['simple'])
    return self.matcher.find_template(
      sc, template, 0.65) is not None

  def get_popular_dish_button_state(self):
    """Return 'select', 'start', 'stop' or None (grey cooldown
    button / dialog not open) for the Popular Dish row button."""
    x = self.sc.popular_dish_button_x
    y = self.sc.popular_dish_button_y
    hw = self.sc.popular_dish_button_roi_half_width_x
    hh = self.sc.popular_dish_button_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    for state, template_key in POPULAR_DISH_BUTTON_TEMPLATES.items():
      if self.matcher.is_hsv_match(roi, template_key, threshold=0.9):
        return state
    return None

  def get_food_delivery_truck_coords(self):
    """Return the tap [x, y] of the truck button when a Food Delivery
    is available (black truck, no counter / countdown), else None."""
    left = self.sc.food_delivery_roi_left_x
    right = self.sc.food_delivery_roi_right_x
    top = self.sc.food_delivery_roi_top_y
    bottom = self.sc.food_delivery_roi_bottom_y
    roi = self._bgr()[top:bottom, left:right]
    loc = self.matcher.match_bgr_sqdiff(
      roi, 'food_delivery_available')
    if loc is None:
      return None
    th = self.matcher.templates[
      'food_delivery_available']['simple'].shape[0]
    return [self.sc.side_button_tap_x, top + loc[1] + th // 2]

  def is_screen_dimmed(self):
    """A dialog dims the white settings gear."""
    x = self.sc.settings_x
    y = self.sc.settings_y
    hw = self.sc.settings_roi_half_width_x
    hh = self.sc.settings_roi_half_height_y
    roi = self._gray()[y - hh:y + hh, x - hw:x + hw]
    return roi.max() < SETTINGS_GEAR_MIN_BRIGHTNESS

  def get_top_bar_line_y(self):
    """Return the y of the top bar's black line (end of the first run
    of black rows in the top band), else None.

    The first run, not the lowest black row: a black row lower in the
    restaurant (e.g. a night city) must not move the spot down. Too
    short runs are skipped; a run reaching the band bottom is no line
    (e.g. a black screen).
    """
    height = self._bgr().shape[0]
    top = round(height * TOP_BAR_BAND_TOP)
    bottom = round(height * TOP_BAR_BAND_BOTTOM)
    band = self._bgr()[top:bottom].max(axis=2) < TOP_BAR_LINE_MAX_VALUE
    black_rows = band.mean(axis=1) > TOP_BAR_LINE_MIN_RATIO
    min_rows = round(TOP_BAR_LINE_MIN_ROWS_Y * self.sc.y_scale)
    run = 0
    for i, black in enumerate(black_rows):
      if black:
        run += 1
      elif run >= min_rows:
        return top + i - 1
      else:
        run = 0
    return None

  def is_having_food_delivery_accept(self):
    """Accept button of the first order in the Food Delivery
    dialog."""
    x = self.sc.food_delivery_accept_x
    y = self.sc.food_delivery_accept_y
    hw = self.sc.food_delivery_accept_roi_half_width_x
    hh = self.sc.food_delivery_accept_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    return self.matcher.is_hsv_match(
      roi, 'food_delivery_accept', threshold=0.9)

  def is_having_helper_available(self):
    """Helper button shows a black person with nothing under it (no
    green work countdown, no ad offer, not grey cooldown)."""
    left = self.sc.helper_roi_left_x
    right = self.sc.helper_roi_right_x
    top = self.sc.helper_roi_top_y
    bottom = self.sc.helper_roi_bottom_y
    roi = self._bgr()[top:bottom, left:right]
    return self.matcher.match_bgr_sqdiff(
      roi, 'helper_available',
      max_diff=HELPER_AVAILABLE_MAX_DIFF) is not None

  def is_having_helper_invite(self):
    """Invite button of the first helper in the "Invite a helper"
    dialog."""
    x = self.sc.helper_invite_x
    y = self.sc.helper_invite_y
    hw = self.sc.helper_invite_roi_half_width_x
    hh = self.sc.helper_invite_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    return self.matcher.is_hsv_match(
      roi, 'helper_invite', threshold=0.8)

  def _is_red_close_at(self, x, y, half_width, half_height):
    """Red X of a dialog / reward summary centered at (x, y)."""
    roi = self._hsv()[y - half_height:y + half_height,
                      x - half_width:x + half_width]
    return self.matcher.color_ratio(
      roi, UPGRADE_BADGE_RED) >= ADVENTURE_CLOSE_RED_MIN_RATIO

  def is_having_events_dialog(self):
    """The "Events" dialog (party popper) is open."""
    return self._is_red_close_at(
      self.sc.events_close_x, self.sc.events_close_y,
      self.sc.dialog_close_roi_half_width_x,
      self.sc.dialog_close_roi_half_height_y)

  def is_having_adventure_level_dialog(self):
    """Level dialog of an adventure is open on top."""
    return self._is_red_close_at(
      self.sc.adventure_level_close_x,
      self.sc.adventure_level_close_y,
      self.sc.dialog_close_roi_half_width_x,
      self.sc.dialog_close_roi_half_height_y)

  def is_having_adventure_reward_screen(self):
    """Full screen reward cards (revealing or the summary)."""
    roi = self._hsv()[
      self.sc.adventure_reward_bg_roi_top_y:
      self.sc.adventure_reward_bg_roi_bottom_y,
      self.sc.adventure_reward_bg_roi_left_x:
      self.sc.adventure_reward_bg_roi_right_x]
    return self.matcher.color_ratio(
      roi, ADVENTURE_REWARD_BG) >= ADVENTURE_REWARD_BG_MIN_RATIO

  def is_having_adventure_summary(self):
    """Summary of the revealed reward cards (all cards revealed)."""
    return self._is_red_close_at(
      self.sc.adventure_summary_close_x,
      self.sc.adventure_summary_close_y,
      self.sc.adventure_summary_close_roi_half_width_x,
      self.sc.adventure_summary_close_roi_half_height_y)

  def is_having_adventure_right_arrow(self):
    """Right arrow of the level dialog: the last level isn't
    selected."""
    x = self.sc.adventure_right_arrow_x
    y = self.sc.adventure_right_arrow_y
    hw = self.sc.adventure_right_arrow_roi_half_width_x
    hh = self.sc.adventure_right_arrow_roi_half_height_y
    roi = self._hsv()[y - hh:y + hh, x - hw:x + hw]
    return self.matcher.color_ratio(
      roi, ADVENTURE_ARROW_BLUE) >= ADVENTURE_ARROW_MIN_RATIO

  def get_adventure_enter_coords(self, key_template):
    """Enter button of the adventure whose key icon is shown in the
    "Events" list (free runs left), else None."""
    left = self.sc.events_list_roi_left_x
    top = self.sc.events_list_roi_top_y
    roi = self._hsv()[top:self.sc.events_list_roi_bottom_y,
                      left:self.sc.events_list_roi_right_x]
    loc = self.matcher.match_hsv(
      roi, key_template, threshold=ADVENTURE_KEY_THRESHOLD)
    if loc is None:
      return None
    th, tw = self.matcher.templates[key_template]['simple'].shape[:2]
    return {
      'x': left + loc[0] + tw // 2 + self.sc.adventure_enter_offset_x,
      'y': top + loc[1] + th // 2 + self.sc.adventure_enter_offset_y,
    }

  def is_having_adventure_key(self, key_template):
    """Key icon on the level dialog's counter (an ad icon there means
    no free run)."""
    roi = self._hsv()[
      self.sc.adventure_counter_roi_top_y:
      self.sc.adventure_counter_roi_bottom_y,
      self.sc.adventure_counter_roi_left_x:
      self.sc.adventure_counter_roi_right_x]
    return self.matcher.is_hsv_match(
      roi, key_template, threshold=ADVENTURE_KEY_THRESHOLD)

  # ── Game actions ──────────────────────────────────────────

  def close_accidental_popups(self):
    """Detect and close any popup with a red X button."""
    cross_loc = self.matcher.match_hsv(
      self._hsv(), 'popup_close_cross')
    if cross_loc:
      tmpl = self.matcher.templates['popup_close_cross']
      th, tw = tmpl['simple'].shape[:2]
      cx = cross_loc[0] + tw // 2
      cy = cross_loc[1] + th // 2
      log.info('Popup detected — closing at (%d, %d)',
               cx, cy)
      self.device.click([cx, cy])
      time.sleep(1)
      self.device.capture_screenshot()
      return True
    return False

  def claim_race_reward(self):
    """Claim the reward of the "Restaurant Race ended!" dialog.

    The dialog has no X, only Claim (gems, no ad), and blocks the
    game. Claim is searched only below the dialog's title, so it can't
    be another dialog's Claim (the Investor's starts an ad). Returns
    True when Claim was tapped.
    """
    title = self.matcher.match_hsv(
      self._hsv(), 'race_ended_title',
      threshold=RACE_TEMPLATE_THRESHOLD)
    if title is None:
      return False
    top = title[1] + self.matcher.templates[
      'race_ended_title']['simple'].shape[0]
    th, tw = self.matcher.templates['race_claim']['simple'].shape[:2]
    below = self._hsv()[top:]
    claim = None
    if below.shape[0] >= th:
      claim = self.matcher.match_hsv(
        below, 'race_claim', threshold=RACE_TEMPLATE_THRESHOLD)
    if claim is None:
      log.warning('Restaurant Race ended, but its Claim not found')
      return False
    button = below[claim[1]:claim[1] + th, claim[0]:claim[0] + tw]
    if button[:, :, 2].mean() < RACE_CLAIM_MIN_BRIGHTNESS:
      log.info('Restaurant Race ended dialog is covered, not claiming')
      return False
    coords = [claim[0] + tw // 2, top + claim[1] + th // 2]
    log.info('Restaurant Race ended - claiming the reward at (%d, %d)',
             coords[0], coords[1])
    key_log.info('RACE - Restaurant Race reward claimed')
    self.device.click(coords)
    time.sleep(RACE_CLAIM_DELAY_S)
    self.device.capture_screenshot()
    return True

  def handle_stale_state(self, nothing_to_update_count,
                         swipe_count):
    """Handle when no actionable items found for too long.

    The game is not restarted: start_app() only brings the running
    game to the foreground. The counter is reset afterwards, so this
    happens once per STALE_RECOVERY_THRESHOLD empty loops, not on
    every loop until something can be upgraded.

    Returns updated (nothing_to_update_count, swipe_count).
    """
    if nothing_to_update_count > STALE_RECOVERY_THRESHOLD:
      log.warning('Nothing to update for %d loops — bringing game to '
                  'foreground.', nothing_to_update_count)
      key_log.info(
        "STALE - Nothing to update, bringing game to foreground")
      self.device.start_app()
      time.sleep(1)
      # A dialog may block the game, e.g. one that came late at start
      # or "Restaurant Race ended!" (no X)
      self.device.capture_screenshot()
      self.claim_race_reward()
      for _ in range(STALE_POPUP_CLOSE_TRIES):
        if not self.close_accidental_popups():
          break
        # The race dialog may have been under the closed popup
        self.claim_race_reward()
      self.device.click(self.loc.null_click_coords)
      time.sleep(1)
      nothing_to_update_count = 0

    if (nothing_to_update_count >= STALE_SWIPE_THRESHOLD
        and nothing_to_update_count % 5 == 0):
      cycle_pos = swipe_count % (SWIPES_PER_DIRECTION * 2)
      coords = (self.loc.swipe_layout_down_coords
                if cycle_pos < SWIPES_PER_DIRECTION
                else self.loc.swipe_layout_up_coords)
      log.info('Stale swipe — scrolling to find items')
      self.device.swipe(**coords)
      time.sleep(3)
      swipe_count += 1

    return nothing_to_update_count, swipe_count

  def reposition_after_new_level(self, food_icon_locations):
    """Swipe layout to position first food icon correctly.

    Called once after a new level starts when food icons
    are first detected.
    """
    log.info('Repositioning layout after new level')
    y_coords = [c[1] for c in food_icon_locations]
    min_y_idx = y_coords.index(min(y_coords))
    swipe_x = food_icon_locations[min_y_idx][0]
    self.device.swipe(
      start={'y': min(y_coords), 'x': swipe_x},
      end={
        'x': swipe_x,
        'y': self.sc.food_icon_tooltip_boundary_y})
    time.sleep(3)
    self.device.start_app()
    time.sleep(3)
    self.device.capture_screenshot()

  def adjust_layout_if_icons_too_high(self,
                                      food_icon_locations):
    """Swipe up if any food icon is too close to the top.

    Returns True if layout was adjusted (caller should
    re-capture and continue).
    """
    for c in food_icon_locations:
      if c[1] <= self.sc.food_icon_top_boundary_y:
        log.info('Adjusting layout — icons too high')
        self.device.swipe(
          **self.loc.swipe_layout_little_up_coords)
        time.sleep(3)
        self.device.start_app()
        time.sleep(1)
        self.device.capture_screenshot()
        return True
    return False

  def try_upgrade_items(self):
    """Buy upgrades when the upgrade button shows its badge.

    Checked on every loop screenshot, so upgrades are bought soon after
    they become affordable.
    """
    if self.is_having_upgrade():
      log.info('Upgrades available — attempting to upgrade')
      self.do_upgrades()
      self.device.capture_screenshot()

  def open_boxes(self):
    """Find and click all visible boxes."""
    screenshot = self._bgr()
    template = self.matcher.templates['box']['simple']
    locations = self.matcher.find_all_templates(
      screenshot, template, end=False, threshold=0.7)

    if len(locations) == 0:
      template = self.matcher.templates['box2']['simple']
      locations = self.matcher.find_all_templates(
        screenshot, template, end=False, threshold=0.7)

    for c in locations:
      log.info('Opening box')
      self.device.click(c)
      time.sleep(0.2)

  def get_food_icon_locations(self):
    """Find all station upgrade icons on screen (none on a screen
    dimmed by a dialog)."""
    matched = self.matcher.find_upgrade_icons(
      self._hsv(), self.sc.upgrade_arrow_min_height_y,
      self.sc.upgrade_arrow_max_height_y)

    danger_max_y = self.loc.danger_max_y
    return [c for c in matched
            if c[1] <= danger_max_y
            and not self._is_near_club_button(c[0], c[1])]

  def _is_near_club_button(self, x, y):
    """Detect food icons whose first station box would overlap the club
    button (bottom-left corner), so they couldn't be opened
    """
    return (x < self.sc.side_button_zone_width_x
            and y > self.sc.club_button_danger_min_y)

  def _keep_away_from_side_buttons(self, x):
    """Nudge x toward the center, away from the side UI buttons
    (restaurant race, food boxes, etc.) pinned to the screen edges.
    """
    margin = self.sc.side_button_zone_width_x
    max_x = self.sc.screen_width - margin
    return max(margin, min(x, max_x))

  def upgrade_food_items(self, food_coords):
    """Click food icons to upgrade them."""
    for c in food_coords[:3]:
      log.info('Upgrading food item at (%d, %d)',
               c[0], c[1])
      self.device.click([
        c[0] + self.sc.upgrade_click_shift_x,
        c[1] + self.sc.upgrade_food_offset_y
        + self.sc.upgrade_click_shift_y])
      time.sleep(0.2)

      hold_x = self._keep_away_from_side_buttons(
        c[0] + self.sc.better_food_pos_offset_x)
      self.device.click_and_hold(
        hold_x,
        c[1] - self.sc.better_food_neg_offset_y, 3000)
      time.sleep(0.4)

      if c[1] < self.sc.food_icon_tooltip_boundary_y:
        click_x = self._keep_away_from_side_buttons(
          c[0] - self.sc.better_food_neg_offset_x)
        self.device.click([
          click_x, c[1] + self.sc.upgrade_food_offset_y])
      else:
        self.device.click(self.loc.null_click_coords)
      time.sleep(0.2)

  def do_upgrades(self):
    """Open the upgrade menu and buy the first row's upgrade while it
    is affordable, in rounds of UPGRADE_CLICKS_PER_CHECK taps."""
    # A station popup may still be open after upgrade_food_items(); a
    # tap on the upgrade button would only close it
    self.device.click(self.loc.null_click_coords)
    time.sleep(STATION_POPUP_CLOSE_DELAY_S)
    self.device.click(self.loc.upgrade_button_coords)
    time.sleep(UPGRADE_DIALOG_OPEN_DELAY_S)
    self.device.capture_screenshot()
    if not self.is_having_upgrades_dialog():
      # The close tap would land on the restaurant and could open a
      # station popup hiding the food icons, so tap the null spot.
      log.info('Upgrades dialog did not open')
      self.device.click(self.loc.null_click_coords)
      time.sleep(UPGRADE_DIALOG_CLOSE_DELAY_S)
      return
    clicks = 0
    while clicks < UPGRADE_MAX_CLICKS:
      if clicks:
        self.device.capture_screenshot()
      if not self.is_first_upgrade_affordable():
        break
      for _ in range(UPGRADE_CLICKS_PER_CHECK):
        self.device.click(
          self.loc.single_upgrade_button_coords)
        time.sleep(0.2)
      clicks += UPGRADE_CLICKS_PER_CHECK
    log.info('Upgrade taps: %d', clicks)
    self.device.click(self.loc.close_upgrade_button_coords)
    time.sleep(UPGRADE_DIALOG_CLOSE_DELAY_S)

  def open_chests(self):
    """Recursively open all available chests."""
    log.info('Checking for chests')
    time.sleep(1)
    self.device.capture_screenshot()
    time.sleep(1)
    if self.is_having_chest_icon():
      log.info('Chest found — opening')
      self.device.click(self.loc.chest_coords)
      time.sleep(2)
      self.device.click(self.loc.chest_coords)
      time.sleep(1)
      self.device.click(self.loc.chest_coords)
      time.sleep(1)
      self.device.click(self.loc.chest_coords)
      time.sleep(1)
      self.device.click(self.loc.close_chest_button_coords)
      time.sleep(1)
      self.open_chests()

  def check_to_go_next_level(self):
    """Check and execute level transition if available.

    Returns True if moved to a new level.
    """
    gone_to_next_level = False

    if self.is_having_next_level_icon():
      log.info('Renovating to next level')
      self.device.click(self.loc.next_level_button_coords)
      time.sleep(2)
      self.device.click(self.loc.renovate_button_coords)
      self._wait_and_click_open_button()
      gone_to_next_level = True
      key_log.info("NEXT LEVEL - Renovated to next level")

    elif self.is_having_fly_next_city_icon():
      self.device.click(self.loc.next_level_button_coords)
      time.sleep(2)
      log.info('Flying to next city')
      self.device.click(
        self.loc.fly_next_city_button_coords)
      self._wait_and_click_welcome_okay()
      self._wait_and_click_open_button()
      time.sleep(5)
      gone_to_next_level = True
      key_log.info("FLY - Flying to next city")

    if gone_to_next_level:
      self.open_chests()

    return gone_to_next_level

  def _wait_and_click_welcome_okay(self):
    """Wait for the "Okay" button of the "Welcome to <city>" dialog
    and tap it."""
    self._wait_and_click_button(
      'Okay', self.is_having_welcome_city_okay,
      self.loc.welcome_city_ok_button_coords,
      WELCOME_OKAY_TIMEOUT_S)

  def _wait_and_click_open_button(self):
    """Wait for the "Open" button of the first stand and tap it."""
    self._wait_and_click_button(
      'Open', self.is_having_open_button,
      self.loc.first_lemonade_stand_open_coords,
      OPEN_BUTTON_TIMEOUT_S)

  def _wait_and_click_button(self, name, is_visible, coords,
                             timeout_s):
    """Wait for a dialog button and tap it.

    If it doesn't show up in time, tap its position anyway and log
    a warning, the bot then continues.
    """
    deadline = time.monotonic() + timeout_s
    while True:
      self.device.capture_screenshot()
      if is_visible():
        time.sleep(DIALOG_BUTTON_TAP_DELAY_S)
        break
      if time.monotonic() >= deadline:
        log.warning(
          '%s button not found within %d s, tapping it blindly. '
          'This should not normally happen.', name, timeout_s)
        key_log.warning("WARNING - %s button not found", name)
        break
      time.sleep(1)
    self.device.click(coords)

  def select_popular_dish(self):
    """Select the first dish as Popular Dish, start the skill and
    stop it right away.

    The skill effect is not used, only the selection counts for
    the Masterchef quest. Returns True when the skill was stopped,
    i.e. its cooldown has started.
    """
    # The button goes select -> start -> stop -> grey (cooldown).
    # Each step continues from the state found, so an attempt
    # interrupted earlier is finished as well.
    state = self._tap_and_get_popular_dish_button_state(
      self.loc.skills_circle_coords)
    if state == 'select':
      state = self._choose_first_dish()
    if state == 'start':
      state = self._tap_and_get_popular_dish_button_state(
        self.loc.popular_dish_button_coords)
    stopped = False
    if state == 'stop':
      stopped = self._tap_and_get_popular_dish_button_state(
        self.loc.popular_dish_button_coords) is None

    if stopped:
      log.info('Popular Dish selected and stopped')
      key_log.info("POPULAR DISH - Selected first dish")
    else:
      log.info('Popular Dish not selected (button: %s)', state)
    self._close_skill_dialogs()
    return stopped

  def _choose_first_dish(self):
    """Open "Select a dish" and tap the first selectable dish.

    Returns the Popular Dish button state afterwards, 'start' when
    a dish was chosen.
    """
    self.device.click(self.loc.popular_dish_button_coords)
    time.sleep(SKILL_DIALOG_DELAY_S)
    for coords in self.loc.first_dish_coords_candidates:
      state = self._tap_and_get_popular_dish_button_state(coords)
      if state == 'start':
        return state
    log.info('No dish to select yet (no stand open)')
    return None

  def _tap_and_get_popular_dish_button_state(self, coords):
    self.device.click(coords)
    time.sleep(SKILL_DIALOG_DELAY_S)
    self.device.capture_screenshot()
    return self.get_popular_dish_button_state()

  def _close_skill_dialogs(self):
    """Close "Select a dish" and "Active Skills" if open."""
    self.device.capture_screenshot()
    for _ in range(2):
      if not self.close_accidental_popups():
        break

  def accept_food_delivery(self, truck_coords):
    """Open Food Delivery and accept the first order.

    Used mainly to complete a quest. The dialog closes by itself after
    Accept. Returns True when the order was accepted.
    """
    self.device.click(truck_coords)
    time.sleep(FOOD_DELIVERY_DIALOG_DELAY_S)
    self.device.capture_screenshot()
    if not self.is_having_food_delivery_accept():
      log.info('Food Delivery dialog not found')
      self.close_accidental_popups()
      return False
    self.device.click(self.loc.food_delivery_accept_coords)
    time.sleep(FOOD_DELIVERY_DIALOG_DELAY_S)
    self.device.capture_screenshot()
    if self.is_having_food_delivery_accept():
      log.info('Food Delivery dialog still open after Accept')
      self.close_accidental_popups()
      return False
    log.info('Food Delivery accepted (first order)')
    return True

  def invite_helper(self):
    """Open "Invite a helper" and invite the first helper.

    The helper works for ~4 min, then the button offers an ad (never
    tapped) and a ~30 min cooldown follows. The dialog closes by
    itself after Invite. Returns True when the helper was invited.
    """
    # Confirm on a fresh screenshot, so a frame caught between two
    # states (e.g. countdown -> ad offer) doesn't tap the ad offer
    time.sleep(1)
    self.device.capture_screenshot()
    if not self.is_having_helper_available():
      log.info('Helper button no longer available')
      return False
    self.device.click(self.loc.helper_button_coords)
    if not self._wait_for_helper_invite():
      log.info('Invite a helper dialog not found')
      self.close_accidental_popups()
      return False
    self.device.click(self.loc.helper_invite_coords)
    time.sleep(HELPER_DIALOG_DELAY_S)
    self.device.capture_screenshot()
    if self.is_having_helper_invite():
      log.info('Invite a helper dialog still open after Invite')
      self.close_accidental_popups()
      return False
    log.info('Helper invited (first helper)')
    return True

  def _wait_for_helper_invite(self):
    deadline = time.monotonic() + HELPER_DIALOG_TIMEOUT_S
    while time.monotonic() < deadline:
      time.sleep(1)
      self.device.capture_screenshot()
      if self.is_having_helper_invite():
        return True
    return False

  def collect_adventure_rewards(self):
    """Collect the free Adventures rewards (Zeus' Feast, Hangry
    Pirates).

    Opens "Events" (party popper), scrolls to the Adventures at its
    bottom and, for each adventure with a key icon, completes its last
    level while the counter shows a key. An ad icon means the free
    runs are used up; it is never tapped. Returns False when a screen
    didn't show up as expected (the dialogs are then closed).
    """
    collected = {}
    finished = self._collect_adventures(collected)
    if collected:
      key_log.info('ADVENTURES - Collected rewards: %s', ', '.join(
        f'{name} {runs}x' for name, runs in collected.items()))
    if not finished:
      self._close_adventure_dialogs()
    return finished

  def _collect_adventures(self, collected):
    """Collect all adventures; count the runs in collected
    {name: runs}."""
    self.device.capture_screenshot()
    if not self.is_having_settings():
      log.warning('Adventures: main screen not found')
      return False
    self.device.click(self.loc.events_button_coords)
    time.sleep(ADVENTURE_DIALOG_DELAY_S)
    self.device.capture_screenshot()
    if not self.is_having_events_dialog():
      log.warning('Adventures: Events dialog not found')
      return False
    scroll = self.loc.events_scroll_coords
    self.device.swipe(scroll['start'], scroll['end'])
    time.sleep(ADVENTURE_DIALOG_DELAY_S)
    for name, list_key, dialog_key in ADVENTURES:
      self.device.capture_screenshot()
      if not self.is_having_events_dialog():
        log.warning('Adventures: Events dialog not found')
        return False
      enter_coords = self.get_adventure_enter_coords(list_key)
      if enter_coords is None:
        log.info('Adventures: %s has no free run', name)
        continue
      self.device.click(enter_coords)
      time.sleep(ADVENTURE_DIALOG_DELAY_S)
      if not self._complete_adventure_levels(
          name, dialog_key, collected):
        return False
      log.info('Adventures: %s completed %dx',
               name, collected.get(name, 0))
      if not self._close_adventure_dialog(
          self.is_having_adventure_level_dialog,
          self.loc.adventure_level_close_coords):
        return False
    return self._close_adventure_dialog(
      self.is_having_events_dialog, self.loc.events_close_coords)

  def _complete_adventure_levels(self, name, key_template, collected):
    """Complete the last level while the counter shows a key.

    Bonus key cards add runs, so the count is not known in advance.
    Every run is counted in collected. Returns False on an unexpected
    screen.
    """
    for _ in range(ADVENTURE_MAX_RUNS):
      self.device.capture_screenshot()
      if not self.is_having_adventure_level_dialog():
        log.warning('Adventures: level dialog not found')
        return False
      if not self._select_last_adventure_level():
        return False
      if not self.is_having_adventure_key(key_template):
        return True
      self.device.click(self.loc.adventure_complete_last_coords)
      time.sleep(ADVENTURE_DIALOG_DELAY_S)
      if not self._reveal_adventure_rewards():
        return False
      collected[name] = collected.get(name, 0) + 1
    return True

  def _close_adventure_dialog(self, is_open, close_coords):
    """Tap the dialog's X if the dialog is open."""
    self.device.capture_screenshot()
    if not is_open():
      log.warning('Adventures: dialog to close not found')
      return False
    self.device.click(close_coords)
    time.sleep(ADVENTURE_DIALOG_DELAY_S)
    return True

  def _select_last_adventure_level(self):
    """Tap the right arrow until the last level is selected."""
    for _ in range(ADVENTURE_MAX_ARROW_TAPS):
      if not self.is_having_adventure_right_arrow():
        return True
      self.device.click(self.loc.adventure_right_arrow_coords)
      time.sleep(ADVENTURE_DIALOG_DELAY_S)
      self.device.capture_screenshot()
    log.warning('Adventures: last level not reached')
    return False

  def _reveal_adventure_rewards(self):
    """Tap the reward cards until the summary shows, then close it.

    Every tap is preceded by a check of the reward screen, so a tap
    never lands on anything else (e.g. an ad).
    """
    if not self._wait_for_adventure_reward_screen():
      log.warning('Adventures: reward screen not found')
      return False
    for _ in range(ADVENTURE_MAX_REVEAL_TAPS):
      self.device.capture_screenshot()
      if not self.is_having_adventure_reward_screen():
        log.warning('Adventures: reward screen not found')
        return False
      summary = self.is_having_adventure_summary()
      # A tap reveals the next card, on the summary it closes it
      self.device.click(self.loc.adventure_reveal_tap_coords)
      time.sleep(ADVENTURE_REVEAL_DELAY_S)
      if summary:
        return True
    log.warning('Adventures: reward summary not found')
    return False

  def _wait_for_adventure_reward_screen(self):
    """Wait for the reward screen after "Complete last level"."""
    deadline = time.monotonic() + ADVENTURE_REWARD_TIMEOUT_S
    while time.monotonic() < deadline:
      self.device.capture_screenshot()
      if self.is_having_adventure_reward_screen():
        return True
      time.sleep(1)
    return False

  def _close_adventure_dialogs(self):
    """Close the screens left open by a failed collection.

    The reward cards have no X: they are tapped through like in a run
    (each tap after a check of the reward screen), then the level and
    Events dialogs are closed by their red X.
    """
    for _ in range(ADVENTURE_MAX_REVEAL_TAPS + 1):
      self.device.capture_screenshot()
      if not self.is_having_adventure_reward_screen():
        break
      self.device.click(self.loc.adventure_reveal_tap_coords)
      time.sleep(ADVENTURE_REVEAL_DELAY_S)
    for _ in range(3):
      self.device.capture_screenshot()
      if not self.close_accidental_popups():
        return

  def redeem_investor(self):
    """Find and claim investor reward."""
    redeem_button_coords = {
      'x': self.sc.redeem_investor_reward_x,
      'y': self.sc.redeem_investor_reward_y}
    log.info('Finding investor')
    mc = None

    sc = self._gray()
    template = \
      self.matcher.templates['small_investor_icon']['grayscale']
    mc = self.matcher.find_template(sc, template)
    if mc:
      self.device.click([
        mc[0] + self.sc.small_investor_click_offset_x,
        mc[1] + self.sc.small_investor_click_offset_y])
    else:
      sc = self.matcher.apply_investor_mask(self._bgr())
      template = self.matcher.apply_investor_mask(
        self.matcher.templates['investor']['simple'])
      mc = self.matcher.find_template(sc, template, 0.65)
      if mc:
        self.device.click([
          mc[0] + self.sc.large_investor_click_offset_x,
          mc[1] + self.sc.large_investor_click_offset_y])

    if mc:
      log.info('Found investor')
      time.sleep(2)
      log.info('Now claiming')
      self.device.click(redeem_button_coords)
      time.sleep(5)
      self.device.start_app()
      time.sleep(2)

  def run_full_boost_ads(self):
    """Watch multiple ads for full boost."""
    btn_coords = {
      'x': self.sc.ad_button_x,
      'y': self.sc.ad_button_y}
    time.sleep(1)
    for _ in range(12):
      log.info('Clicking ad button')
      self.device.click(btn_coords)
      time.sleep(5)
      self.device.start_app()
      log.info('App started after ad')
      time.sleep(5)

  def run_ad(self):
    """Watch a single ad."""
    btn_coords = {
      'x': self.sc.ad_button_x,
      'y': self.sc.ad_button_y}
    time.sleep(5)
    log.info('Clicking ad button')
    self.device.click(btn_coords)
    time.sleep(5)
    self.device.start_app()
    log.info('App started after ad')
    time.sleep(1)

  # ── Init / login ──────────────────────────────────────────

  def init_game(self):
    """Wait until game is in playable state.

    Taps known dialogs that can cover the screen when the bot is
    restarted, e.g. right after a renovation or a flight, and closes
    other dialogs by their red X (e.g. "While you were away...").
    Then watches for dialogs that come late.
    """
    while True:
      self.device.capture_screenshot()
      if self.is_having_settings():
        break
      if self.is_having_offline_earnings():
        self.device.click(
          self.loc.close_offline_earnings_coords)
        break
      if self.is_having_welcome_city_okay():
        log.info('Init: closing "Welcome to <city>" dialog')
        self._wait_and_click_welcome_okay()
        continue
      if self.is_having_open_button():
        log.info('Init: tapping first stand "Open" button')
        self._wait_and_click_open_button()
        continue
      if self.claim_race_reward():
        continue
      if self.close_accidental_popups():
        continue
      log.info('Init: waiting for game to be ready')
      time.sleep(5)
    log.info('Init: game is ready')
    self._close_late_start_dialogs()

  def _close_late_start_dialogs(self):
    """Watch the screen for START_DIALOGS_WATCH_S and close dialogs
    that dim it."""
    log.info('Init: watching %d s for late start dialogs',
             START_DIALOGS_WATCH_S)
    deadline = time.monotonic() + START_DIALOGS_WATCH_S
    while time.monotonic() < deadline:
      time.sleep(START_DIALOGS_CHECK_S)
      self.device.capture_screenshot()
      if self.is_screen_dimmed():
        log.info('Init: late start dialog, closing it')
        self._close_dimming_dialogs()

  def place_null_click_below_top_bar(self):
    """Place the null spot just below the top bar's black line.

    Called once at start. The status bar height differs between
    phones, so the spot can't be derived from the resolution. If the
    line is not found, the fallback from coords.py stays and an ERROR
    is logged.
    """
    if not self._close_dimming_dialogs():
      self._log_null_spot_fallback('screen stays dimmed by a dialog')
      return
    line_y = self.get_top_bar_line_y()
    if line_y is None:
      self._log_null_spot_fallback('no black line in the top band')
      return
    coords = self.loc.null_click_coords
    coords['y'] = line_y + round(
      NULL_CLICK_BELOW_TOP_BAR_Y * self.sc.y_scale)
    log.info('Null spot below the top bar (y=%d): (%d, %d)',
             line_y, coords['x'], coords['y'])

  def _close_dimming_dialogs(self):
    """Close dialogs that dim the screen (on a dimmed screen the line
    comes out wrong). Returns True when the screen is not dimmed."""
    # init_game() may have just tapped a dialog that is fading out
    time.sleep(1)
    self.device.capture_screenshot()
    for _ in range(DIMMING_DIALOG_CLOSE_TRIES):
      if not self.is_screen_dimmed():
        return True
      if self.is_having_welcome_city_okay():
        log.info('Start: closing "Welcome to <city>" dialog')
        self._wait_and_click_welcome_okay()
      elif self.is_having_open_button():
        log.info('Start: tapping first stand "Open" button')
        self._wait_and_click_open_button()
      elif self.claim_race_reward():
        pass
      elif not self.close_accidental_popups():
        # A tap outside a modal dialog closes it and doesn't reach the
        # restaurant behind it (Back doesn't close dialogs)
        log.info('Start: dimmed screen without a red X, tapping '
                 'outside the dialog')
        self.device.click(self.loc.null_click_coords)
      time.sleep(1)
      self.device.capture_screenshot()
    return not self.is_screen_dimmed()

  def _log_null_spot_fallback(self, reason):
    coords = self.loc.null_click_coords
    log.error(
      'Top bar not found (%s), the null spot stays at the fallback '
      '(%d, %d) from coords.py. Risky: if the top bar covers it, '
      'station popups stay open; if it is too low, it can hit a '
      'customer bubble, open the Investor dialog and start an ad. Fix: '
      'check a screenshot of this phone and adjust '
      'place_null_click_below_top_bar() in game_actions.py.',
      reason, coords['x'], coords['y'])
    key_log.error(
      "ERROR - Top bar not found (%s), null spot at fallback "
      "(%d, %d), popups may stay open or an ad may start; fix "
      "place_null_click_below_top_bar()",
      reason, coords['x'], coords['y'])

  def start_game_for_first_time(self):
    """Handle first-time game startup dialogs."""
    is_notification_closed = False
    is_first_stand_closed = False
    while True:
      log.info('Checking game state')
      self.device.capture_screenshot()
      if (not is_notification_closed
          and self.is_having_notification()):
        log.info('found notification')
        self.device.click(
          self.loc.close_nofication_coords)
        is_notification_closed = True
        continue
      elif (not is_first_stand_closed
            and self.is_having_first_lemonade_stand_open()):
        log.info('found first stand')
        self.device.click(
          self.loc.first_lemonade_stand_open_coords)
        is_notification_closed = True
        is_first_stand_closed = True
        continue
      elif self.is_having_settings():
        log.info('found settings')
        self.device.click(self.loc.settings_coords)
        is_notification_closed = True
        is_first_stand_closed = True
        break
      time.sleep(5)
