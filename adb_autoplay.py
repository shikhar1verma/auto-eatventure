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

    # def capture_screenshot(self):
    #     pilimg = self.device.screenshot()
    #     pilimg.save(self.captured_sc_path)
    #     self.current_cv2_sc = cv2.imread(self.captured_sc_path)
    #     self.current_cv2_sc_grayscale = cv2.imread(
    #         self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
    #     self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
    #         self.current_cv2_sc, cv2.COLOR_BGR2HSV)
    #     return

    def capture_screenshot(self):
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

    def is_having_no_boost_indicator_2x(self):
        return self.is_image_template_matching(self.matching_templates_cv2['no_boost_indicator_2x'], 0.92)

    def is_having_fly_next_city_icon(self):
        return self.is_image_template_matching(self.matching_templates_cv2['fly_next_city_icon'])

    def is_having_small_investor_icon(self):
        return self.is_bnw_image_template_matching(self.matching_templates_cv2['small_investor_icon'])

    def is_having_investor(self):
        return self.is_investor_image_template_matching(self.matching_templates_cv2['investor'], 0.65)

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
            screenshot, template, end=True)
        return matched_coordinates

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
        if mc:
            template = self.matching_templates_cv2['small_investor_icon']['grayscale']
            mc = self.find_template(sc, template)
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
            time.sleep(1)
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

    def check_to_go_next_level(self):
        if dev.is_having_next_level_icon():
            dev.click(loc.next_level_button_coords)
            time.sleep(0.2)
            dev.click(loc.renovate_button_coords)
            time.sleep(10)
            dev.click(loc.first_lemonade_stand_open_coords)
        elif dev.is_having_fly_next_city_icon():
            dev.click(loc.next_level_button_coords)
            time.sleep(0.2)
            dev.click(loc.fly_next_city_button_coords)
            time.sleep(15)
            dev.click(loc.welcome_city_ok_button_coords)
            time.sleep(5)
            dev.click(loc.first_lemonade_stand_open_coords)
            time.sleep(5)
        return

    def upgrade_food_items(self, coords):
        for c in coords[:3]:  # as mostly after 3 no food icon is visible
            dev.click([c[0], c[1] + 30])
            time.sleep(0.2)

            # hack for better food button
            y_neg_offset = 150
            dev.click_and_hold(c[0], c[1] - y_neg_offset, 800)
            time.sleep(0.2)
            dev.click(loc.null_click_coords)
            time.sleep(0.2)
        return

    def open_boxes(self):
        coords = dev.get_all_boxes_locations()
        for c in coords:
            dev.click(c)
            time.sleep(0.2)
        return

    def do_upgrades(self):
        dev.click(loc.upgrade_button_coords)
        time.sleep(0.3)
        for i in range(5):
            dev.click(loc.single_upgrade_button_coords)
            time.sleep(0.2)
        dev.click(loc.close_upgrade_button_coords)
        return


class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        print(f"{self.name} elapsed time: {elapsed_time} seconds\n")


dev = AutoEatventure()

dev.start_app()

# below code is for first time opening game
# is_notification_closed = False
# is_first_stand_closed = False
# while True:
#     print('checking ')
#     dev.capture_screenshot()
#     if not is_notification_closed and dev.is_having_notification():
#         print('found notification')
#         dev.click(close_nofication_coords)
#         is_notification_closed = True
#         continue
#     elif not is_first_stand_closed and dev.is_having_first_lemonade_stand_open():
#         print('found first stand')
#         dev.click(first_lemonade_stand_open_coords)
#         is_notification_closed = True
#         is_first_stand_closed = True
#         continue
#     elif dev.is_having_settings():
#         print('found settings')
#         dev.click(settings_coords)
#         is_notification_closed = True
#         is_first_stand_closed = True
#         break

#     time.sleep(5)

# print('Found settings was success')

# first time login with cloud save
# time.sleep(1)
# dev.click(settings_coords)
# time.sleep(1)
# dev.click(cloud_save_coords)
# time.sleep(1)
# dev.click(email_input_coords)
# time.sleep(3)
# dev.input_text(os.getenv('EMAIL'))
# time.sleep(1)
# dev.click(text_ok_button_coords)
# time.sleep(1)
# dev.click(password_input_coords)
# time.sleep(3)
# dev.input_text(os.getenv('PASSWORD'))
# time.sleep(1)
# dev.click(text_ok_button_coords)
# time.sleep(1)
# dev.click(login_button_coords)
# time.sleep(8) # loading cloud save
# dev.click(use_cloud_save_button_coords)
# time.sleep(8) # for loading game
# dev.click(close_game_for_restart_button_coords)

# INTIALIZATION OF GAME CHECK
while True:
    dev.capture_screenshot()
    if dev.is_having_settings():
        break
    if dev.is_having_offline_earnings():
        dev.click(loc.close_offline_earnings_coords)
        break

    time.sleep(5)

# dev.run_full_boost_ads()

# MAIN LOGIC
count = 0
start_time = time.time()
pause = False
while True:
    count += 1

    with Timer("Capturing screenshot"):
        dev.capture_screenshot()

    # check for investor
    if count % 3 == 0:
        with Timer("Redeem investor"):
            dev.redeem_investor()

    # check for ads
    if count == 1 or count % 100 == 0:  # every 100th iteration
        with Timer("Running full boost ads"):
            print('Checking for boost')
            if dev.is_having_no_boost_indicator_2x():
                print('running ads')
                dev.run_full_boost_ads()
                time.sleep(2)

    # maind upgrades
    # upgrade click
    with Timer("Upgrading items"):
        if count % 5 == 0 and dev.is_having_upgrade():
            print('Upgrading items')
            dev.do_upgrades()
            dev.capture_screenshot()

    if count == 1 or count % 2 == 0:
        with Timer("Finding boxes"):
            # boxes find and click
            print('finding boxes')
            dev.open_boxes()

    with Timer("Finding food icons"):
        # dev.capture_screenshot()
        print('finding food icons')
        coords = dev.get_all_better_food_icon_locations()
    if len(coords) != 0:
        # c = random.choice(coords)
        with Timer("Clicking food icons"):
            random.shuffle(coords)
            dev.upgrade_food_items(coords)
    else:
        if count % 10 == 0:
            # next level check
            print('next level check')
            dev.check_to_go_next_level()


# collect full boost
# time.sleep(2)
# with Timer("Running full boost ads"):
#     for i in range(12):
#         dev.run_ads()


# run ads and close it
# for i in range(30):
#   if dev.is_having_ad_cross():
#     btn_coords = dev.get_ad_cross_button()
#     if btn_coords:
#       dev.click(btn_coords)
#       break
#   time.sleep(5)

# print(dev.is_having_ad_cross())

# for annotating points
# print(len(coords))
# print('coords', coords)
# sc = cv2.imread(dev.captured_sc_path)
# for c in coords:
#     cv2.circle(sc, (c[0], c[1]), radius=10,
#                 color=(0, 0, 255), thickness=-1)
# cv2.imwrite('./captured_screenshots_on_the_fly/annotated_screenshot.png', sc)
