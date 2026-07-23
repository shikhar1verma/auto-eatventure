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
SWIPES_PER_DIRECTION = 5
STALE_RESTART_THRESHOLD = 50
STALE_SWIPE_THRESHOLD = 15


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
    return self.matcher.is_hsv_match(
      self._hsv(), 'upgrade_button', threshold=0.97)

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

  def handle_stale_state(self, nothing_to_update_count,
                         swipe_count):
    """Handle when no actionable items found for too long.

    Returns updated swipe_count.
    """
    if nothing_to_update_count > STALE_RESTART_THRESHOLD:
      log.warning('Nothing to update — restarting app.')
      key_log.info("RESTART - Stale state, restarting app")
      self.device.start_app()
      time.sleep(1)
      self.device.click(self.loc.null_click_coords)
      time.sleep(1)

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

    return swipe_count

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

  def try_upgrade_items(self, count, new_level_started):
    """Attempt upgrades every 5th iteration.

    Returns updated new_level_started flag.
    """
    if count % 5 == 0 and self.is_having_upgrade():
      log.info('Upgrades available — attempting to upgrade')
      if new_level_started:
        self.do_upgrades(upgrade_count=50)
        new_level_started = False
      else:
        self.do_upgrades()
      self.device.capture_screenshot()
    return new_level_started

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
    """Find all food upgrade icons on screen."""
    screenshot = self._gray()
    template = \
      self.matcher.templates['buy_better_food_icon']['grayscale']
    matched = self.matcher.find_all_templates(
      screenshot, template, end=False, threshold=0.8)

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

  def do_upgrades(self, upgrade_count=10):
    """Open upgrade menu and click upgrade N times."""
    self.device.click(self.loc.upgrade_button_coords)
    time.sleep(0.3)
    for _ in range(upgrade_count):
      self.device.click(
        self.loc.single_upgrade_button_coords)
      time.sleep(0.2)
    self.device.click(self.loc.close_upgrade_button_coords)

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
      time.sleep(10)
      self.device.click(
        self.loc.first_lemonade_stand_open_coords)
      gone_to_next_level = True
      key_log.info("NEXT LEVEL - Renovated to next level")

    elif self.is_having_fly_next_city_icon():
      self.device.click(self.loc.next_level_button_coords)
      time.sleep(2)
      log.info('Flying to next city')
      self.device.click(
        self.loc.fly_next_city_button_coords)
      time.sleep(15)
      self.device.click(
        self.loc.welcome_city_ok_button_coords)
      time.sleep(5)
      self.device.click(
        self.loc.first_lemonade_stand_open_coords)
      time.sleep(5)
      gone_to_next_level = True
      key_log.info("FLY - Flying to next city")

    if gone_to_next_level:
      self.open_chests()

    return gone_to_next_level

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
    """Wait until game is in playable state."""
    while True:
      self.device.capture_screenshot()
      if self.is_having_settings():
        break
      if self.is_having_offline_earnings():
        self.device.click(
          self.loc.close_offline_earnings_coords)
        break
      time.sleep(5)

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
