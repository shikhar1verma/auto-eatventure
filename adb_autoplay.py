import constants as loc
import cv2
from adbutils import adb
import time
import numpy as np
from sklearn.cluster import DBSCAN
import random
import os
import io
import subprocess
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


class AutoEatventure:
    def __init__(self):
        self.device = adb.device()
        self.package_name = "com.hwqgrhhjfd.idlefastfood"
        self.notification_message = 'Allow Eatventure to send you notifications?'
        self.captured_sc_path = './captured_screenshots_on_the_fly/screenshot.png'
        self.current_cv2_sc = None
        self.current_cv2_sc_grayscale = None
        self.current_cv2_sc_bgr2hsv = None
        self.matching_screenshots_path = {
            'notification': './matching_screenshots/notification.png',
            'first_lemondae_stand_open': './matching_screenshots/first_lemonade_stand_open.png',
            'settings': './matching_screenshots/settings.png',
            'offline_earnings': './matching_screenshots/offline_earnings.png',
            'upgrade_button': './matching_screenshots/upgrade_button.png',
            'single_upgrade': './matching_screenshots/single_upgrade.png',
            'box': './matching_screenshots/box.png',
            'box2': './matching_screenshots/box2.png',
            'buy_better_food_icon': './matching_screenshots/buy_better_food_icon.png',
            'buy_better_food_button': './matching_screenshots/buy_better_food_button.png',
            'go_next_level': './matching_screenshots/go_next_level_icon.png',
            'no_boost_indicator_2x': './matching_screenshots/no_boost_indicator_2x.png',
            'fly_next_city_icon': './matching_screenshots/fly_next_city_icon.png',
            'small_investor_icon': './matching_screenshots/small_investor_icon.png',
            'investor': './matching_screenshots/investor.png',
            'chest_icon': './matching_screenshots/chest_icon.png',
            'ads_crosses': {
                'cross1': './matching_screenshots/ads_crosses/cross1.png',
            }
        }
        self.matching_templates_cv2 = {}
        self.load_templates()

    def load_templates(self):
        # {
        #     'notification': {
        #         'simple': '',
        #         'grayscale': '',
        #         'bgr2hsv': ''
        #     }
        # }
        for key, value in self.matching_screenshots_path.items():
            if key == 'ads_crosses':
                self.matching_templates_cv2[key] = {}
                for k, v in value.items():
                    simple = cv2.imread(v)
                    self.matching_templates_cv2[key][k] = {
                        'simple': simple,
                        'grayscale': cv2.imread(v, cv2.IMREAD_GRAYSCALE),
                        'bgr2hsv': cv2.cvtColor(simple, cv2.COLOR_BGR2HSV)
                    }
            else:
                simple = cv2.imread(value)
                self.matching_templates_cv2[key] = {
                    'simple': simple,
                    'grayscale': cv2.imread(value, cv2.IMREAD_GRAYSCALE),
                    'bgr2hsv': cv2.cvtColor(simple, cv2.COLOR_BGR2HSV)
                }

    def start_app(self):
        self.device.shell(
            f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1")
        return

    def close_app(self):
        self.device.shell(f"am force-stop {self.package_name}")
        return

    def capture_screenshot_on_disk(self):
        """Capture screenshot and save on disk
        """
        pilimg = self.device.screenshot()
        pilimg.save(self.captured_sc_path)
        self.current_cv2_sc = cv2.imread(self.captured_sc_path)
        self.current_cv2_sc_grayscale = cv2.imread(
            self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
        self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
            self.current_cv2_sc, cv2.COLOR_BGR2HSV)
        return

    def capture_screenshot(self):
        """In memory capture screenshot
        """
        # pilimg = self.device.screenshot()
        adb_command = f'adb -s {self.device.serial} shell screencap -p'
        output = subprocess.check_output(adb_command.split())

        # Convert the output to a PIL Image object
        pilimg = Image.open(io.BytesIO(output))
        pilimg.load()
        pilimg = pilimg.convert("RGB")

        # # Convert PIL image to numpy array (OpenCV format)
        open_cv_image = np.array(pilimg)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR

        self.current_cv2_sc = open_cv_image
        self.current_cv2_sc_grayscale = cv2.cvtColor(
            open_cv_image, cv2.COLOR_BGR2GRAY)
        self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
            open_cv_image, cv2.COLOR_BGR2HSV)
        return

    def find_template(self, image, template, threshold=0.8):
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        matches = cv2.minMaxLoc(result)
        print(matches)
        _, max_val, _, max_loc = matches

        if max_val > threshold:
            return max_loc
        return None

    def find_all_templates(self, image, template, end=False, threshold=0.8):
        if len(template.shape[::-1]) == 2:
            template_width, template_height = template.shape[::-1]
        else:
            template_width, template_height = template.shape[::-1][1:]
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        # looking at best position
        m = cv2.minMaxLoc(result)
        print(m)
        locations = np.where(result >= threshold)

        coordinates = []
        for pt in zip(*locations[::-1]):
            if end:
                x_center = pt[0] + template_width
                y_center = pt[1] + template_height
            else:
                x_center = pt[0] + template_width//2
                y_center = pt[1] + template_height//2
            coordinates.append((x_center, y_center))

        # cluster the points together
        # Use DBSCAN clustering to group close points
        coords = np.array(coordinates)
        if len(coords) == 0:
            return []
        dbscan = DBSCAN(eps=10, min_samples=5)
        dbscan.fit(coords)

        # Find the cluster centroids
        centroids = []
        for cluster_label in set(dbscan.labels_):
            if cluster_label != -1:  # Ignore the noise points (label -1)
                cluster_coords = coords[dbscan.labels_ == cluster_label]
                centroid = np.mean(cluster_coords, axis=0)
                centroids.append(centroid)

        centroids = [c.astype(int).tolist() for c in centroids]
        return centroids

    def is_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        hsv_sc = self.current_cv2_sc_bgr2hsv
        hsv_template = template_cv_imgs['bgr2hsv']
        matched_coordinates = self.find_template(
            hsv_sc, hsv_template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def is_bnw_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        screenshot = self.current_cv2_sc_grayscale
        template = template_cv_imgs['grayscale']
        matched_coordinates = self.find_template(
            screenshot, template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def is_investor_image_template_matching(self, template_cv_imgs: dict, threshold=0.8):
        screenshot = self.apply_investor_mask(self.current_cv2_sc)
        template = self.apply_investor_mask(template_cv_imgs['simple'])
        matched_coordinates = self.find_template(
            screenshot, template, threshold=threshold)
        if matched_coordinates:
            return True
        return False

    def apply_investor_mask(self, image, tolerance=15):
        # cap = ['#696548', '#776F4B', '#8B8350', '#87804D']
        colors = [(26, 80, 105), (25, 94, 119), (26, 108, 139), (26, 110, 135)]
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros_like(hsv_image[:, :, 0])

        for color in colors:
            lower_color = np.array(
                [max(color[0] - tolerance, 0), max(color[1] - tolerance, 0), max(color[2] - tolerance, 0)])
            upper_color = np.array([min(color[0] + tolerance, 180),
                                    min(color[1] + tolerance, 255), min(color[2] + tolerance, 255)])

            mask = cv2.inRange(hsv_image, lower_color, upper_color)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
        return masked_image

    def apply_box_mask(self, image, tolerance=2):
        # box = ['#FFE18B', '#AB7245', '#8C5E37', '#E8BB72', '#FED080']
        # colors = [(22, 116, 255),
        #           (13, 152, 171),
        #           (14, 155, 140),
        #           (19, 130, 232),
        #           (19, 126, 254),
        #           (18, 130, 239)]
        colors = [(13, 152, 171),
                  (14, 155, 140)]
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros_like(hsv_image[:, :, 0])

        for color in colors:
            lower_color = np.array(
                [max(color[0] - tolerance, 0), max(color[1] - tolerance, 0), max(color[2] - tolerance, 0)])
            upper_color = np.array([min(color[0] + tolerance, 180),
                                    min(color[1] + tolerance, 255), min(color[2] + tolerance, 255)])

            mask = cv2.inRange(hsv_image, lower_color, upper_color)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
        return masked_image

    def convert_to_binary(self, im_gray, threshold=128):
        im_bw = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)[1]
        return im_bw

    def annotate_points(self, coords):
        # for annotating points
        print(len(coords))
        print('coords', coords)
        sc = cv2.imread(dev.captured_sc_path)
        for c in coords:
            cv2.circle(sc, (c[0], c[1]), radius=10,
                       color=(0, 0, 255), thickness=-1)
        cv2.imwrite(
            './captured_screenshots_on_the_fly/annotated_screenshot.png', sc)
        return
    
    def is_pixel_color_present_between_coordinates(self, start_coords, end_coords, color_to_check):
        """this function check if in image two coordinates in img having some color or not.

        Args:
            start_coords (dict): {x: 1, y: 22} Dictionary of x and y coordinates of a points. 
            end_coords (dict): {x: 1, y: 22} Dictionary of x and y coordinates of a points.
            color_to_check (list): [1, 3 , 4] RGB/BGR color that needs to be checked. 
        """
        # Get the coordinates of the points on the line between (x1, y1) and (x2, y2)
        line_points = []
        x1, y1 = start_coords['x'], start_coords['y']
        x2, y2 = end_coords['x'], end_coords['y']
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        x_increment = dx / steps
        y_increment = dy / steps

        for i in range(steps + 1):
            x = int(x1 + i * x_increment)
            y = int(y1 + i * y_increment)
            line_points.append((x, y))

        # Check if the specified color is present in the pixels along the line
        color_present = False

        for x, y in line_points:
            pixel_color = self.current_cv2_sc[y, x]
            if all(pixel_color == color_to_check):
                color_present = True
                break

        return color_present



    def is_having_notification(self):
        return self.is_image_template_matching(self.matching_templates_cv2['notification'])

    def is_having_first_lemonade_stand_open(self):
        return self.is_image_template_matching(self.matching_templates_cv2['first_lemondae_stand_open'])

    def is_having_settings(self):
        return self.is_image_template_matching(self.matching_templates_cv2['settings'])

    def is_having_offline_earnings(self):
        return self.is_image_template_matching(self.matching_templates_cv2['offline_earnings'])

    def is_having_upgrade(self):
        return self.is_image_template_matching(self.matching_templates_cv2['upgrade_button'])

    def is_having_single_upgrade(self):
        return self.is_image_template_matching(self.matching_templates_cv2['single_upgrade'])

    def is_having_box(self):
        return self.is_image_template_matching(self.matching_templates_cv2['box'])

    def is_having_better_food_icon(self):
        return self.is_image_template_matching(self.matching_templates_cv2['buy_better_food_icon'])

    def is_having_better_food_button(self):
        return self.is_image_template_matching(self.matching_templates_cv2['buy_better_food_button'])

    def is_having_next_level_icon(self):
        return self.is_image_template_matching(self.matching_templates_cv2['go_next_level'])

    def is_having_ad_cross(self):
        return self.is_image_template_matching(self.matching_templates_cv2['ads_crosses']['cross1'])

    def is_having_no_boost_indicator(self):
        x1, y1 = 408, 274
        x2, y2 = 466, 274
        start = {'x': x1, 'y': y1}
        end = {'x': x2, 'y': y2}
        color_to_check = [42, 192, 255]
        # here we checking if yellow color is present in pixels where boost x2 is written
        # if yellow color not present it means is having no boost indicator
        return not self.is_pixel_color_present_between_coordinates(start, end, color_to_check)

    def is_having_no_boost_indicator_2x(self):
        return self.is_image_template_matching(self.matching_templates_cv2['no_boost_indicator_2x'], 0.92)

    def is_having_fly_next_city_icon(self):
        return self.is_image_template_matching(self.matching_templates_cv2['fly_next_city_icon'])

    def is_having_small_investor_icon(self):
        return self.is_bnw_image_template_matching(self.matching_templates_cv2['small_investor_icon'])

    def is_having_investor(self):
        return self.is_investor_image_template_matching(self.matching_templates_cv2['investor'], 0.65)

    def is_having_chest_icon(self):
        return self.is_image_template_matching(self.matching_templates_cv2['chest_icon'])

    def get_all_boxes_locations(self):
        # screenshot = self.convert_to_binary(
        #     self.current_cv2_sc_grayscale, threshold=150)
        # template = self.convert_to_binary(
        #     self.matching_templates_cv2['box']['grayscale'], threshold=150)
        screenshot = self.apply_box_mask(self.current_cv2_sc)
        template = self.apply_box_mask(
            self.matching_templates_cv2['box']['simple'])
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # matched_coordinates = self.find_all_templates(hsv_sc, hsv_template)
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=False)
        if len(matched_coordinates) != 0:
            return matched_coordinates

        # this is for a little different box
        template = self.apply_box_mask(
            self.matching_templates_cv2['box2']['simple'])
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=False)

        return matched_coordinates

    def get_all_better_food_icon_locations(self):
        screenshot = self.current_cv2_sc_grayscale
        template = self.matching_templates_cv2['buy_better_food_icon']['grayscale']
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # matched_coordinates = self.find_all_templates(hsv_sc, hsv_template)
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=False, threshold=0.8)

        safe_matched_coordinates = []
        danger_y_max = 2690
        for c in matched_coordinates:
            if c[1] <= danger_y_max:
                safe_matched_coordinates.append(c)

        return safe_matched_coordinates

    def get_better_food_button(self):
        hsv_sc = self.current_cv2_sc_bgr2hsv
        hsv_template = self.matching_templates_cv2['buy_better_food_button']['bgr2hsv']
        matched_coordinates = self.find_template(hsv_sc, hsv_template)
        return matched_coordinates

    def redeem_investor(self):
        redeem_button_coords = {
            'x': 720,
            'y': 2020
        }
        print('Finding investor')
        mc = None

        # for small investor icon
        sc = self.current_cv2_sc_grayscale
        template = self.matching_templates_cv2['small_investor_icon']['grayscale']
        mc = self.find_template(sc, template)
        if mc:
            self.click([mc[0]+10, mc[1]+10])
        else:
            sc = self.apply_investor_mask(self.current_cv2_sc)
            template = self.apply_investor_mask(
                self.matching_templates_cv2['investor']['simple'])
            mc = self.find_template(sc, template, 0.65)
            if mc:
                self.click([mc[0]+55, mc[1]+100])

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
        screenshot = self.current_cv2_sc_grayscale
        template = self.matching_templates_cv2['ads_crosses']['cross1']['grayscale']
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        matched_coordinates = self.find_template(screenshot, template)
        return matched_coordinates

    def click(self, coords):
        if type(coords) is dict:
            self.device.shell(f"input tap {coords['x']} {coords['y']}")
        if type(coords) is list:
            self.device.shell(f"input tap {coords[0]} {coords[1]}")
        return

    def click_and_hold(self, x, y, hold_duration=1000):  # hold duration in milliseconds
        self.device.shell(
            f'input swipe {x} {y} {x} {y} {hold_duration}')
        return

    def input_text(self, text):
        # Escape special characters and spaces
        escaped_text = text.replace(" ", "%s").replace(
            "&", "\\&").replace("|", "\\|")
        self.device.shell(f"input text '{escaped_text}'")
        return

    def swipe(self, start, end):
        self.device.swipe(start['x'], start['y'], end['x'], end['y'])
        return

    def run_full_boost_ads(self):
        btn_coords = {
            'x': 720,
            'y': 2950
        }
        time.sleep(1)
        with Timer("Running full boost ads"):
            for i in range(12):
                print('click ad button')
                self.click(btn_coords)
                # time.sleep(60)
                time.sleep(5)
                self.start_app()
                print('app started')
                time.sleep(5)
        return

    def run_ad(self):
        btn_coords = {
            'x': 720,
            'y': 2950
        }
        time.sleep(5)
        print('click ad button')
        self.click(btn_coords)
        # time.sleep(60)
        time.sleep(5)
        self.start_app()
        print('app started')
        time.sleep(1)
        return

    def open_chests(self):
        print('Checking for chests')
        # taking screenshot as state changed.
        time.sleep(1)
        self.capture_screenshot()
        time.sleep(1)
        if self.is_having_chest_icon():
            print('Chest found now opening.')
            # actually icon is clicked to open chest
            self.click(loc.chest_coords)
            time.sleep(2)
            # just opening chest item
            self.click(loc.chest_coords)
            time.sleep(1)
            # just opening chest item
            self.click(loc.chest_coords)
            time.sleep(1)
            # last extra click
            self.click(loc.chest_coords)
            time.sleep(1)
            self.click(loc.close_chest_button_coords)
            time.sleep(1)
            self.open_chests()
        return

    def check_to_go_next_level(self):
        gone_to_next_level = False
        if self.is_having_next_level_icon():
            self.click(loc.next_level_button_coords)
            time.sleep(2)
            self.click(loc.renovate_button_coords)
            time.sleep(10)
            self.click(loc.first_lemonade_stand_open_coords)
            gone_to_next_level = True
        elif self.is_having_fly_next_city_icon():
            self.click(loc.next_level_button_coords)
            time.sleep(2)
            self.click(loc.fly_next_city_button_coords)
            time.sleep(15)
            self.click(loc.welcome_city_ok_button_coords)
            time.sleep(5)
            self.click(loc.first_lemonade_stand_open_coords)
            time.sleep(5)
            gone_to_next_level = True

        if gone_to_next_level:
            with Timer('Time to open chests'):
                self.open_chests()

        return gone_to_next_level

    def upgrade_food_items(self, coords):
        for c in coords[:3]:  # as mostly after 3 no food icon is visible
            self.click([c[0], c[1] + 30])
            time.sleep(0.2)

            # hack for better food button
            y_neg_offset = 130
            x_pos_offset = 20
            self.click_and_hold(c[0] + x_pos_offset, c[1] - y_neg_offset, 1200)
            time.sleep(0.4)
            if c[1] < 1240:  # to avoid null zone overlapping with tooltip
                self.click([c[0] - 110, c[1] + 30])
            else:
                self.click(loc.null_click_coords)
            time.sleep(0.2)
        return

    def open_boxes(self):
        coords = self.get_all_boxes_locations()
        for c in coords:
            self.click(c)
            time.sleep(0.2)
        return

    def do_upgrades(self, upgrade_count=10):
        self.click(loc.upgrade_button_coords)
        time.sleep(0.3)
        for i in range(upgrade_count):
            self.click(loc.single_upgrade_button_coords)
            time.sleep(0.2)
        self.click(loc.close_upgrade_button_coords)
        return

    def login_with_cloud(self):
        # first time login with cloud save
        time.sleep(1)
        self.click(loc.settings_coords)
        time.sleep(1)
        self.click(loc.cloud_save_coords)
        time.sleep(1)
        self.click(loc.email_input_coords)
        time.sleep(3)
        self.input_text(os.getenv('EMAIL'))
        time.sleep(1)
        self.click(loc.text_ok_button_coords)
        time.sleep(1)
        self.click(loc.password_input_coords)
        time.sleep(3)
        self.input_text(os.getenv('PASSWORD'))
        time.sleep(1)
        self.click(loc.text_ok_button_coords)
        time.sleep(1)
        self.click(loc.login_button_coords)
        time.sleep(8)  # loading cloud save
        self.click(loc.use_cloud_save_button_coords)
        time.sleep(8)  # for loading game
        self.click(loc.close_game_for_restart_button_coords)
        return

    def start_game_for_first_time(self):
        # below code is for first time opening game
        is_notification_closed = False
        is_first_stand_closed = False
        while True:
            print('checking ')
            self.capture_screenshot()
            if not is_notification_closed and self.is_having_notification():
                print('found notification')
                self.click(loc.close_nofication_coords)
                is_notification_closed = True
                continue
            elif not is_first_stand_closed and self.is_having_first_lemonade_stand_open():
                print('found first stand')
                self.click(loc.first_lemonade_stand_open_coords)
                is_notification_closed = True
                is_first_stand_closed = True
                continue
            elif self.is_having_settings():
                print('found settings')
                self.click(loc.settings_coords)
                is_notification_closed = True
                is_first_stand_closed = True
                break
            time.sleep(5)
        return

    def init_game(self):
        """To check if game is in playing state
        """
        # INTIALIZATION OF GAME CHECK
        while True:
            self.capture_screenshot()
            if self.is_having_settings():
                break
            if self.is_having_offline_earnings():
                self.click(loc.close_offline_earnings_coords)
                break

            time.sleep(5)
        return

    def start_playing_game(self):
        count = 0
        # to orient first food icon in better place for faster gameplay
        new_level_first_food_icon_swipe = False
        new_level_started = True
        swipping_pattern = [
            loc.swipe_layout_down_coords, loc.swipe_layout_down_coords, loc.swipe_layout_down_coords,
            loc.swipe_layout_up_coords, loc.swipe_layout_up_coords, loc.swipe_layout_up_coords
        ]
        swipe_count = 0
        nothing_to_update_count = 0
        while True:
            count += 1
            if nothing_to_update_count > 50:
                print('Nothing to update max limit reached. Brute force to resolved this infinity loop.')
                self.start_app()
                print('starting app')
                time.sleep(1)
                self.click(loc.null_click_coords)
                time.sleep(1)

            # this logic is to move the layout up and down when not update icons shows
            print('nothing_to_update_count', nothing_to_update_count)
            if nothing_to_update_count >= 15 and nothing_to_update_count % 5 == 0:
                print('swipe count', swipe_count)
                print('len(swipping_pattern)', len(swipping_pattern))
                print('swiping pattern index', swipe_count %
                      len(swipping_pattern))
                swipping_coords = swipping_pattern[swipe_count % len(
                    swipping_pattern)]
                self.swipe(**swipping_coords)
                print('##############################',
                      swipe_count, swipping_coords)
                time.sleep(3)
                swipe_count += 1

            with Timer("Capturing screenshot"):
                self.capture_screenshot()

            # check for investor
            if count % 3 == 0:
                with Timer("Redeem investor"):
                    self.redeem_investor()

            # check for ads
            if count == 1 or count % 100 == 0:  # every 100th iteration
                with Timer("Running full boost ads"):
                    print('Checking for boost')
                    if self.is_having_no_boost_indicator(): # this is for users didn't buy 2x permanent boost
                        print('running ads')
                        self.run_full_boost_ads()
                        time.sleep(2)
                    
                    # a quick fix for boost but will run multiple times in many scenarios
                    if self.is_having_no_boost_indicator_2x():
                        print('running ads for 2x users')
                        self.run_full_boost_ads()
                        time.sleep(2)


            # maind upgrades
            # upgrade click
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
                    # boxes find and click
                    print('finding boxes')
                    self.open_boxes()

            with Timer("Finding food icons"):
                # self.capture_screenshot()
                print('finding food icons')
                coords = self.get_all_better_food_icon_locations()

            if len(coords) > 0 and not new_level_first_food_icon_swipe:
                y_coords = [c[1] for c in coords]
                swipe_x_coords = coords[y_coords.index(min(y_coords))][0]
                self.swipe(
                    start={
                        'y': min(y_coords), 
                        'x': swipe_x_coords}, 
                    end={
                        'x': swipe_x_coords, 
                        'y': 1300}
                )
                new_level_first_food_icon_swipe = True
                time.sleep(3)
                # to avoid any infinite scenario
                self.start_app()
                print('starting app')
                time.sleep(3)
                self.capture_screenshot()
                continue

            # this if is for fetching the danger food items and adjust layout to avoid them.
            if len(coords) > 0:
                nothing_to_update_count = 0
                is_danger_food_item = False
                for c in coords:
                    y = c[1]
                    if y <= 1100:
                        is_danger_food_item = True
                        self.swipe(**loc.swipe_layout_little_up_coords)
                        time.sleep(3)
                        # to avoid any infinite scenario
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
                # c = random.choice(coords)
                with Timer("Clicking food icons"):
                    random.shuffle(coords)
                    self.upgrade_food_items(coords)
            else:
                if count % 10 == 0:
                    # next level check
                    print('next level check')
                    gone_to_next_level = self.check_to_go_next_level()
                    if gone_to_next_level:
                        print(
                            '########################swipe count is next level', swipe_count)
                        swipe_count = 0
                        nothing_to_update_count = 0
                        new_level_first_food_icon_swipe = False
                        new_level_started = True


class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        print(f"{self.name} elapsed time: {elapsed_time} seconds\n")


# start the game app.
dev = AutoEatventure()
dev.start_app()

# to check if game is playable.
dev.init_game()

# MAIN LOGIC
dev.start_playing_game()
