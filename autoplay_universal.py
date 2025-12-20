"""
Universal Auto-Eatventure - Works with both Android and iOS

This is the main automation script that uses the device driver abstraction
to work with both Android (ADB) and iOS (Appium/WebDriverAgent) devices.

Usage:
    # Android (default)
    python autoplay_universal.py

    # iOS
    PLATFORM=ios python autoplay_universal.py

    # Or set in .env file:
    # PLATFORM=ios
"""

import cv2
import time
import numpy as np
from sklearn.cluster import DBSCAN
import random
import os
from PIL import Image

from config import Config, Platform, get_config
from device_driver import DeviceDriver


class AutoEatventure:
    def __init__(self, config: Config = None):
        self.config = config or get_config()
        self.loc = self.config.get_constants_module()

        # Create the appropriate driver
        self.driver: DeviceDriver = self.config.create_driver()

        # Connect to device
        if not self.driver.connect():
            raise RuntimeError(f"Failed to connect to {self.config.platform.value} device")

        self.package_name = self.config.get_app_identifier()
        self.notification_message = 'Allow Eatventure to send you notifications?'
        self.captured_sc_path = './captured_screenshots_on_the_fly/screenshot.png'
        self.current_cv2_sc = None
        self.current_cv2_sc_grayscale = None
        self.current_cv2_sc_bgr2hsv = None

        # Template paths - iOS uses different folder
        template_folder = './matching_screenshots'
        if self.config.platform == Platform.IOS:
            ios_folder = './matching_screenshots_ios'
            if os.path.exists(ios_folder):
                template_folder = ios_folder
            else:
                print(f"Warning: iOS template folder not found at {ios_folder}")
                print("Using Android templates - you should create iOS-specific templates")

        # iOS-specific settings
        self.skip_ads = self.config.platform == Platform.IOS  # Skip ads on iOS
        self.skip_notifications = self.config.platform == Platform.IOS  # iOS handles separately
        self.skip_offline_earnings = self.config.platform == Platform.IOS

        self.matching_screenshots_path = {
            'settings': self._find_template(template_folder, 'settings'),
            'upgrade_button': self._find_template(template_folder, 'upgrade_button'),
            'single_upgrade': self._find_template(template_folder, 'single_upgrade'),
            'box': self._find_template(template_folder, 'box'),
            'box2': self._find_template(template_folder, 'box2'),
            'buy_better_food_icon': self._find_template(template_folder, 'buy_better_food_icon'),
            'buy_better_food_button': self._find_template(template_folder, 'buy_better_food_button'),
            'go_next_level': self._find_template(template_folder, 'go_next_level_icon'),
            'fly_next_city_icon': self._find_template(template_folder, 'fly_next_city_icon'),
            'small_investor_icon': self._find_template(template_folder, 'small_investor_icon'),
            'investor': self._find_template(template_folder, 'investor'),
            'chest_icon': self._find_template(template_folder, 'chest_icon'),
            # Only needed for Android
            'notification': self._find_template(template_folder, 'notification'),
            'first_lemondae_stand_open': self._find_template(template_folder, 'first_lemonade_stand_open'),
            'offline_earnings': self._find_template(template_folder, 'offline_earnings'),
            'no_boost_indicator_2x': self._find_template(template_folder, 'no_boost_indicator_2x'),
            'ads_crosses': {
                'cross1': self._find_template(f'{template_folder}/ads_crosses', 'cross1'),
            }
        }
        self.matching_templates_cv2 = {}
        self.load_templates()

        print(f"AutoEatventure initialized for {self.config.platform.value}")

    def _find_template(self, folder: str, name: str) -> str:
        """Find template file, checking for both .png and .jpg extensions."""
        for ext in ['.png', '.jpg', '.jpeg']:
            path = f'{folder}/{name}{ext}'
            if os.path.exists(path):
                return path
        # Return .png path as default (will show warning later if not found)
        return f'{folder}/{name}.png'

    def load_templates(self):
        """Load all template images for matching."""
        for key, value in self.matching_screenshots_path.items():
            if key == 'ads_crosses':
                self.matching_templates_cv2[key] = {}
                for k, v in value.items():
                    if os.path.exists(v):
                        simple = cv2.imread(v)
                        self.matching_templates_cv2[key][k] = {
                            'simple': simple,
                            'grayscale': cv2.imread(v, cv2.IMREAD_GRAYSCALE),
                            'bgr2hsv': cv2.cvtColor(simple, cv2.COLOR_BGR2HSV)
                        }
                    else:
                        print(f"Warning: Template not found: {v}")
            else:
                if os.path.exists(value):
                    simple = cv2.imread(value)
                    self.matching_templates_cv2[key] = {
                        'simple': simple,
                        'grayscale': cv2.imread(value, cv2.IMREAD_GRAYSCALE),
                        'bgr2hsv': cv2.cvtColor(simple, cv2.COLOR_BGR2HSV)
                    }
                else:
                    print(f"Warning: Template not found: {value}")

    def start_app(self):
        """Launch the game app."""
        self.driver.launch_app(self.package_name)
        return

    def close_app(self):
        """Force close the game app."""
        self.driver.close_app(self.package_name)
        return

    def capture_screenshot_on_disk(self):
        """Capture screenshot and save to disk."""
        pil_image = self.driver.screenshot()
        pil_image.save(self.captured_sc_path)
        self.current_cv2_sc = cv2.imread(self.captured_sc_path)
        self.current_cv2_sc_grayscale = cv2.imread(
            self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
        self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
            self.current_cv2_sc, cv2.COLOR_BGR2HSV)
        return

    def capture_screenshot(self):
        """Capture screenshot in memory."""
        pil_image = self.driver.screenshot()

        # Convert PIL image to numpy array (OpenCV format)
        open_cv_image = np.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR

        self.current_cv2_sc = open_cv_image
        self.current_cv2_sc_grayscale = cv2.cvtColor(
            open_cv_image, cv2.COLOR_BGR2GRAY)
        self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
            open_cv_image, cv2.COLOR_BGR2HSV)
        return

    def find_template(self, image, template, threshold=0.8):
        """Find a single template match in the image."""
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        matches = cv2.minMaxLoc(result)
        print(matches)
        _, max_val, _, max_loc = matches

        if max_val > threshold:
            return max_loc
        return None

    def find_all_templates(self, image, template, end=False, threshold=0.8):
        """Find all template matches using DBSCAN clustering."""
        if len(template.shape[::-1]) == 2:
            template_width, template_height = template.shape[::-1]
        else:
            template_width, template_height = template.shape[::-1][1:]
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        m = cv2.minMaxLoc(result)
        print(m)
        locations = np.where(result >= threshold)

        coordinates = []
        for pt in zip(*locations[::-1]):
            if end:
                x_center = pt[0] + template_width
                y_center = pt[1] + template_height
            else:
                x_center = pt[0] + template_width // 2
                y_center = pt[1] + template_height // 2
            coordinates.append((x_center, y_center))

        coords = np.array(coordinates)
        if len(coords) == 0:
            return []
        dbscan = DBSCAN(eps=10, min_samples=5)
        dbscan.fit(coords)

        centroids = []
        for cluster_label in set(dbscan.labels_):
            if cluster_label != -1:
                cluster_coords = coords[dbscan.labels_ == cluster_label]
                centroid = np.mean(cluster_coords, axis=0)
                centroids.append(centroid)

        centroids = [c.astype(int).tolist() for c in centroids]
        return centroids

    def is_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        """Check if template matches in current screenshot."""
        if not template_cv_imgs:
            return False
        hsv_sc = self.current_cv2_sc_bgr2hsv
        hsv_template = template_cv_imgs['bgr2hsv']
        matched_coordinates = self.find_template(
            hsv_sc, hsv_template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def is_bnw_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        """Check if grayscale template matches."""
        if not template_cv_imgs:
            return False
        screenshot = self.current_cv2_sc_grayscale
        template = template_cv_imgs['grayscale']
        matched_coordinates = self.find_template(
            screenshot, template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def is_investor_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        """Check if investor template matches with color masking."""
        if not template_cv_imgs:
            return False
        screenshot = self.apply_investor_mask(self.current_cv2_sc)
        template = self.apply_investor_mask(template_cv_imgs['simple'])
        matched_coordinates = self.find_template(
            screenshot, template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def apply_investor_mask(self, image, tolerance=15):
        """Apply color mask for investor detection."""
        # Get colors from platform-specific constants if available
        if hasattr(self.loc, 'INVESTOR_COLORS_HSV'):
            colors = self.loc.INVESTOR_COLORS_HSV
            tolerance = getattr(self.loc, 'INVESTOR_COLOR_TOLERANCE', tolerance)
        else:
            colors = [(26, 80, 105), (25, 94, 119), (26, 108, 139), (26, 110, 135)]

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros_like(hsv_image[:, :, 0])

        for color in colors:
            lower_color = np.array(
                [max(color[0] - tolerance, 0), max(color[1] - tolerance, 0),
                 max(color[2] - tolerance, 0)])
            upper_color = np.array([min(color[0] + tolerance, 180),
                                    min(color[1] + tolerance, 255),
                                    min(color[2] + tolerance, 255)])

            mask = cv2.inRange(hsv_image, lower_color, upper_color)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
        return masked_image

    def apply_box_mask(self, image, tolerance=2):
        """Apply color mask for box detection."""
        if hasattr(self.loc, 'BOX_COLORS_HSV'):
            colors = self.loc.BOX_COLORS_HSV
            tolerance = getattr(self.loc, 'BOX_COLOR_TOLERANCE', tolerance)
        else:
            colors = [(13, 152, 171), (14, 155, 140)]

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros_like(hsv_image[:, :, 0])

        for color in colors:
            lower_color = np.array(
                [max(color[0] - tolerance, 0), max(color[1] - tolerance, 0),
                 max(color[2] - tolerance, 0)])
            upper_color = np.array([min(color[0] + tolerance, 180),
                                    min(color[1] + tolerance, 255),
                                    min(color[2] + tolerance, 255)])

            mask = cv2.inRange(hsv_image, lower_color, upper_color)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
        return masked_image

    def convert_to_binary(self, im_gray, threshold=128):
        """Convert grayscale image to binary."""
        im_bw = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)[1]
        return im_bw

    def annotate_points(self, coords):
        """Annotate points on screenshot for debugging."""
        print(len(coords))
        print('coords', coords)
        sc = cv2.imread(self.captured_sc_path)
        for c in coords:
            cv2.circle(sc, (c[0], c[1]), radius=10,
                       color=(0, 0, 255), thickness=-1)
        cv2.imwrite(
            './captured_screenshots_on_the_fly/annotated_screenshot.png', sc)
        return

    def is_pixel_color_present_between_coordinates(self, start_coords, end_coords,
                                                    color_to_check):
        """Check if a specific color is present along a line between two points."""
        line_points = []
        x1, y1 = start_coords['x'], start_coords['y']
        x2, y2 = end_coords['x'], end_coords['y']
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return False
        x_increment = dx / steps
        y_increment = dy / steps

        for i in range(steps + 1):
            x = int(x1 + i * x_increment)
            y = int(y1 + i * y_increment)
            line_points.append((x, y))

        color_present = False
        for x, y in line_points:
            if y < self.current_cv2_sc.shape[0] and x < self.current_cv2_sc.shape[1]:
                pixel_color = self.current_cv2_sc[y, x]
                if all(pixel_color == color_to_check):
                    color_present = True
                    break

        return color_present

    # Detection methods
    def is_having_notification(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('notification'))

    def is_having_first_lemonade_stand_open(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('first_lemondae_stand_open'))

    def is_having_settings(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('settings'))

    def is_having_offline_earnings(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('offline_earnings'))

    def is_having_upgrade(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('upgrade_button'))

    def is_having_single_upgrade(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('single_upgrade'))

    def is_having_box(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('box'))

    def is_having_better_food_icon(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('buy_better_food_icon'))

    def is_having_better_food_button(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('buy_better_food_button'))

    def is_having_next_level_icon(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('go_next_level'))

    def is_having_ad_cross(self):
        ads_crosses = self.matching_templates_cv2.get('ads_crosses', {})
        return self.is_image_template_matching(ads_crosses.get('cross1'))

    def is_having_no_boost_indicator(self):
        """Check if boost is NOT active by looking for yellow color."""
        if hasattr(self.loc, 'BOOST_CHECK_START'):
            start = self.loc.BOOST_CHECK_START
            end = self.loc.BOOST_CHECK_END
            color = getattr(self.loc, 'BOOST_INDICATOR_COLOR_BGR', [42, 192, 255])
        else:
            x1, y1 = 408, 274
            x2, y2 = 466, 274
            start = {'x': x1, 'y': y1}
            end = {'x': x2, 'y': y2}
            color = [42, 192, 255]

        return not self.is_pixel_color_present_between_coordinates(start, end, color)

    def is_having_no_boost_indicator_2x(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('no_boost_indicator_2x'), 0.92)

    def is_having_fly_next_city_icon(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('fly_next_city_icon'))

    def is_having_small_investor_icon(self):
        return self.is_bnw_image_template_matching(
            self.matching_templates_cv2.get('small_investor_icon'))

    def is_having_investor(self):
        return self.is_investor_image_template_matching(
            self.matching_templates_cv2.get('investor'), 0.65)

    def is_having_chest_icon(self):
        return self.is_image_template_matching(
            self.matching_templates_cv2.get('chest_icon'))

    def get_all_boxes_locations(self):
        """Find all box locations in current screenshot."""
        screenshot = self.apply_box_mask(self.current_cv2_sc)
        box_template = self.matching_templates_cv2.get('box')
        if not box_template:
            return []

        template = self.apply_box_mask(box_template['simple'])
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=False)
        if len(matched_coordinates) != 0:
            return matched_coordinates

        box2_template = self.matching_templates_cv2.get('box2')
        if box2_template:
            template = self.apply_box_mask(box2_template['simple'])
            matched_coordinates = self.find_all_templates(
                screenshot, template, end=False)

        return matched_coordinates

    def get_all_better_food_icon_locations(self):
        """Find all food upgrade icon locations."""
        screenshot = self.current_cv2_sc_grayscale
        food_icon = self.matching_templates_cv2.get('buy_better_food_icon')
        if not food_icon:
            return []

        template = food_icon['grayscale']
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=False, threshold=0.65)

        # Get danger zones from constants
        danger_y_max = getattr(self.loc, 'DANGER_Y_MAX', 2690)
        danger_y_min = getattr(self.loc, 'DANGER_Y_MIN', 900)

        safe_matched_coordinates = []
        for c in matched_coordinates:
            # Filter out matches outside the safe zone (top UI and bottom bar)
            if danger_y_min <= c[1] <= danger_y_max:
                safe_matched_coordinates.append(c)

        return safe_matched_coordinates

    def get_better_food_button(self):
        """Find the better food button location."""
        hsv_sc = self.current_cv2_sc_bgr2hsv
        food_button = self.matching_templates_cv2.get('buy_better_food_button')
        if not food_button:
            return None

        hsv_template = food_button['bgr2hsv']
        matched_coordinates = self.find_template(hsv_sc, hsv_template)
        return matched_coordinates

    # Action methods
    def click(self, coords):
        """Click at coordinates."""
        if type(coords) is dict:
            self.driver.tap(coords['x'], coords['y'])
        if type(coords) is list:
            self.driver.tap(coords[0], coords[1])
        return

    def click_and_hold(self, x, y, hold_duration=1000):
        """Long press at coordinates."""
        self.driver.tap_and_hold(x, y, hold_duration)
        return

    def input_text(self, text):
        """Input text."""
        self.driver.input_text(text)
        return

    def swipe(self, start, end):
        """Perform swipe gesture."""
        self.driver.swipe(start['x'], start['y'], end['x'], end['y'])
        return

    def redeem_investor(self):
        """Find and redeem investor rewards."""
        redeem_button_coords = {'x': 720, 'y': 2020}
        if hasattr(self.loc, 'scale_coords'):
            redeem_button_coords = self.loc.scale_coords(redeem_button_coords)

        print('Finding investor')
        mc = None

        # Check for small investor icon
        sc = self.current_cv2_sc_grayscale
        small_investor = self.matching_templates_cv2.get('small_investor_icon')
        if small_investor:
            template = small_investor['grayscale']
            mc = self.find_template(sc, template)
            if mc:
                self.click([mc[0] + 10, mc[1] + 10])

        if not mc:
            investor = self.matching_templates_cv2.get('investor')
            if investor:
                sc = self.apply_investor_mask(self.current_cv2_sc)
                template = self.apply_investor_mask(investor['simple'])
                mc = self.find_template(sc, template, 0.65)
                if mc:
                    self.click([mc[0] + 55, mc[1] + 100])

        if mc:
            print('Found investor')
            time.sleep(2)
            print('Now claiming')
            self.click(redeem_button_coords)
            time.sleep(5)
            self.start_app()
            time.sleep(2)
        return

    def get_ad_cross_button(self):
        """Find the ad close button location."""
        screenshot = self.current_cv2_sc_grayscale
        ads_crosses = self.matching_templates_cv2.get('ads_crosses', {})
        cross1 = ads_crosses.get('cross1')
        if not cross1:
            return None

        template = cross1['grayscale']
        matched_coordinates = self.find_template(screenshot, template)
        return matched_coordinates

    def run_full_boost_ads(self):
        """Watch 12 ads to get full boost."""
        btn_coords = {'x': 720, 'y': 2950}
        if hasattr(self.loc, 'ads_button_coords'):
            btn_coords = self.loc.ads_button_coords

        time.sleep(1)
        with Timer("Running full boost ads"):
            for i in range(12):
                print('click ad button')
                self.click(btn_coords)
                time.sleep(5)
                self.start_app()
                print('app started')
                time.sleep(5)
        return

    def run_ad(self):
        """Watch a single ad."""
        btn_coords = {'x': 720, 'y': 2950}
        if hasattr(self.loc, 'ads_button_coords'):
            btn_coords = self.loc.ads_button_coords

        time.sleep(5)
        print('click ad button')
        self.click(btn_coords)
        time.sleep(5)
        self.start_app()
        print('app started')
        time.sleep(1)
        return

    def open_chests(self):
        """Open any available chests."""
        print('Checking for chests')
        time.sleep(1)
        self.capture_screenshot()
        time.sleep(1)
        if self.is_having_chest_icon():
            print('Chest found now opening.')
            self.click(self.loc.chest_coords)
            time.sleep(2)
            self.click(self.loc.chest_coords)
            time.sleep(1)
            self.click(self.loc.chest_coords)
            time.sleep(1)
            self.click(self.loc.chest_coords)
            time.sleep(1)
            self.click(self.loc.close_chest_button_coords)
            time.sleep(1)
            self.open_chests()
        return

    def check_to_go_next_level(self):
        """Check if we can progress to the next level."""
        gone_to_next_level = False
        if self.is_having_next_level_icon():
            self.click(self.loc.next_level_button_coords)
            time.sleep(2)
            self.click(self.loc.renovate_button_coords)
            time.sleep(10)
            self.click(self.loc.first_lemonade_stand_open_coords)
            gone_to_next_level = True
        elif self.is_having_fly_next_city_icon():
            self.click(self.loc.next_level_button_coords)
            time.sleep(2)
            self.click(self.loc.fly_next_city_button_coords)
            time.sleep(15)
            self.click(self.loc.welcome_city_ok_button_coords)
            time.sleep(5)
            self.click(self.loc.first_lemonade_stand_open_coords)
            time.sleep(5)
            gone_to_next_level = True

        if gone_to_next_level:
            with Timer('Time to open chests'):
                self.open_chests()

        return gone_to_next_level

    def upgrade_food_items(self, coords):
        """Upgrade food items at given coordinates."""
        for c in coords[:3]:
            self.click([c[0], c[1] + 30])
            time.sleep(0.2)

            y_neg_offset = 130
            x_pos_offset = 20
            self.click_and_hold(c[0] + x_pos_offset, c[1] - y_neg_offset, 1200)
            time.sleep(0.4)

            danger_y_min = getattr(self.loc, 'DANGER_Y_MIN', 1240)
            if c[1] < danger_y_min:
                self.click([c[0] - 110, c[1] + 30])
            else:
                self.click(self.loc.null_click_coords)
            time.sleep(0.2)
        return

    def open_boxes(self):
        """Find and open all visible boxes."""
        coords = self.get_all_boxes_locations()
        for c in coords:
            self.click(c)
            time.sleep(0.2)
        return

    def do_upgrades(self, upgrade_count=10):
        """Open upgrade menu and do upgrades."""
        self.click(self.loc.upgrade_button_coords)
        time.sleep(0.3)
        for i in range(upgrade_count):
            self.click(self.loc.single_upgrade_button_coords)
            time.sleep(0.2)
        self.click(self.loc.close_upgrade_button_coords)
        return

    def login_with_cloud(self):
        """Login with cloud save."""
        time.sleep(1)
        self.click(self.loc.settings_coords)
        time.sleep(1)
        self.click(self.loc.cloud_save_coords)
        time.sleep(1)
        self.click(self.loc.email_input_coords)
        time.sleep(3)
        self.input_text(self.config.email)
        time.sleep(1)
        self.click(self.loc.text_ok_button_coords)
        time.sleep(1)
        self.click(self.loc.password_input_coords)
        time.sleep(3)
        self.input_text(self.config.password)
        time.sleep(1)
        self.click(self.loc.text_ok_button_coords)
        time.sleep(1)
        self.click(self.loc.login_button_coords)
        time.sleep(8)
        self.click(self.loc.use_cloud_save_button_coords)
        time.sleep(8)
        self.click(self.loc.close_game_for_restart_button_coords)
        return

    def start_game_for_first_time(self):
        """Handle first-time game startup dialogs."""
        # Skip notification handling on iOS (handled by OS)
        is_notification_closed = self.skip_notifications
        is_first_stand_closed = False
        while True:
            print('checking ')
            self.capture_screenshot()
            if not is_notification_closed and self.is_having_notification():
                print('found notification')
                self.click(self.loc.close_nofication_coords)
                is_notification_closed = True
                continue
            elif not is_first_stand_closed and self.is_having_first_lemonade_stand_open():
                print('found first stand')
                self.click(self.loc.first_lemonade_stand_open_coords)
                is_notification_closed = True
                is_first_stand_closed = True
                continue
            elif self.is_having_settings():
                print('found settings')
                self.click(self.loc.settings_coords)
                is_notification_closed = True
                is_first_stand_closed = True
                break
            time.sleep(5)
        return

    def init_game(self):
        """Wait for game to be in playable state."""
        while True:
            self.capture_screenshot()
            if self.is_having_settings():
                break
            # Skip offline earnings check on iOS
            if not self.skip_offline_earnings and self.is_having_offline_earnings():
                self.click(self.loc.close_offline_earnings_coords)
                break
            # On iOS, just wait for settings icon to appear
            if self.skip_offline_earnings:
                time.sleep(2)
                break
            time.sleep(5)
        return

    def start_playing_game(self):
        """Main game automation loop."""
        count = 0
        new_level_first_food_icon_swipe = False
        new_level_started = True
        swipping_pattern = [
            self.loc.swipe_layout_down_coords, self.loc.swipe_layout_down_coords,
            self.loc.swipe_layout_down_coords,
            self.loc.swipe_layout_up_coords, self.loc.swipe_layout_up_coords,
            self.loc.swipe_layout_up_coords
        ]
        swipe_count = 0
        nothing_to_update_count = 0

        while True:
            count += 1
            if nothing_to_update_count > 50:
                print('Nothing to update max limit reached. Brute force to resolve.')
                self.start_app()
                print('starting app')
                time.sleep(1)
                self.click(self.loc.null_click_coords)
                time.sleep(1)

            print('nothing_to_update_count', nothing_to_update_count)
            if nothing_to_update_count >= 15 and nothing_to_update_count % 5 == 0:
                print('swipe count', swipe_count)
                print('len(swipping_pattern)', len(swipping_pattern))
                swipping_coords = swipping_pattern[swipe_count % len(swipping_pattern)]
                self.swipe(**swipping_coords)
                print('##############################', swipe_count, swipping_coords)
                time.sleep(3)
                swipe_count += 1

            with Timer("Capturing screenshot"):
                self.capture_screenshot()

            # Check for investor
            if count % 3 == 0:
                with Timer("Redeem investor"):
                    self.redeem_investor()

            # Check for ads (skip on iOS)
            if not self.skip_ads and (count == 1 or count % 100 == 0):
                with Timer("Running full boost ads"):
                    print('Checking for boost')
                    if self.is_having_no_boost_indicator():
                        print('running ads')
                        self.run_full_boost_ads()
                        time.sleep(2)

                    if self.is_having_no_boost_indicator_2x():
                        print('running ads for 2x users')
                        self.run_full_boost_ads()
                        time.sleep(2)

            # Upgrade click
            with Timer("Upgrading items"):
                if count % 5 == 0 and self.is_having_upgrade():
                    print('Upgrading items')
                    if new_level_started:
                        self.do_upgrades(upgrade_count=50)
                        new_level_started = False
                    else:
                        self.do_upgrades()
                    self.capture_screenshot()

            if count == 1 or count % 2 == 0:
                with Timer("Finding boxes"):
                    print('finding boxes')
                    self.open_boxes()

            with Timer("Finding food icons"):
                print('finding food icons')
                coords = self.get_all_better_food_icon_locations()

            if len(coords) > 0 and not new_level_first_food_icon_swipe:
                y_coords = [c[1] for c in coords]
                swipe_x_coords = coords[y_coords.index(min(y_coords))][0]
                self.swipe(
                    start={'y': min(y_coords), 'x': swipe_x_coords},
                    end={'x': swipe_x_coords, 'y': 1300}
                )
                new_level_first_food_icon_swipe = True
                time.sleep(3)
                self.start_app()
                print('starting app')
                time.sleep(3)
                self.capture_screenshot()
                continue

            danger_y_min = getattr(self.loc, 'DANGER_Y_MIN', 1100)
            if len(coords) > 0:
                nothing_to_update_count = 0
                is_danger_food_item = False
                for c in coords:
                    y = c[1]
                    if y <= danger_y_min:
                        is_danger_food_item = True
                        self.swipe(**self.loc.swipe_layout_little_up_coords)
                        time.sleep(3)
                        self.start_app()
                        print('starting app')
                        time.sleep(1)
                        break
                if is_danger_food_item:
                    self.capture_screenshot()
                    continue

            if len(coords) == 0:
                nothing_to_update_count += 1
            else:
                nothing_to_update_count = 0

            if len(coords) != 0:
                with Timer("Clicking food icons"):
                    random.shuffle(coords)
                    self.upgrade_food_items(coords)
            else:
                if count % 10 == 0:
                    print('next level check')
                    gone_to_next_level = self.check_to_go_next_level()
                    if gone_to_next_level:
                        print('########################swipe count is next level', swipe_count)
                        swipe_count = 0
                        nothing_to_update_count = 0
                        new_level_first_food_icon_swipe = False
                        new_level_started = True

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.disconnect()


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        print(f"{self.name} elapsed time: {elapsed_time} seconds\n")


def main():
    """Main entry point."""
    config = get_config()
    print(f"Starting Auto-Eatventure for {config.platform.value}")

    dev = None
    try:
        dev = AutoEatventure(config)
        dev.start_app()
        dev.init_game()
        dev.start_playing_game()
    except KeyboardInterrupt:
        print("\nStopping automation...")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if dev:
            dev.cleanup()


if __name__ == "__main__":
    main()
