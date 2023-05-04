import cv2
from adbutils import adb
import time
import numpy as np
from sklearn.cluster import DBSCAN
import random
import os
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
            'buy_better_food_icon': './matching_screenshots/buy_better_food_icon.png',
            'buy_better_food_button': './matching_screenshots/buy_better_food_button.png',
            'go_next_level': './matching_screenshots/go_next_level_icon.png',
            'no_boost_indicator_2x': './matching_screenshots/no_boost_indicator_2x.png',
            'ads_crosses': {
                'cross1': './matching_screenshots/ads_crosses/cross1.png',
            }
        }
        self.matching_templates_cv2 = {}
        # {
        #     'notification': {
        #         'simple': '',
        #         'grayscale': '',
        #         'bgr2hsv': ''
        #     }
        # }

        self.load_templates()

    def load_templates(self):
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

    def capture_screenshot(self):
        pilimg = self.device.screenshot()
        pilimg.save(self.captured_sc_path)
        self.current_cv2_sc = cv2.imread(self.captured_sc_path)
        self.current_cv2_sc_grayscale = cv2.imread(
            self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
        self.current_cv2_sc_bgr2hsv = cv2.cvtColor(
            self.current_cv2_sc, cv2.COLOR_BGR2HSV)
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
        template_width, template_height = template.shape[::-1]
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

    def is_image_template_matching(self, template_cv_imgs: dict):
        hsv_sc = self.current_cv2_sc_bgr2hsv
        hsv_template = template_cv_imgs['bgr2hsv']
        matched_coordinates = self.find_template(hsv_sc, hsv_template)
        if matched_coordinates:
            return True
        return False

    def is_bnw_image_template_matching(self, template_cv_imgs: dict):
        screenshot = self.current_cv2_sc_grayscale
        template = template_cv_imgs['grayscale']
        matched_coordinates = self.find_template(screenshot, template)
        if matched_coordinates:
            return True
        return False

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
        return self.is_image_template_matching(self.matching_templates_cv2['no_boost_indicator_2x'])

    def get_all_boxes_locations(self):
        screenshot = self.current_cv2_sc_grayscale
        template = self.matching_templates_cv2['box']['grayscale']
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # matched_coordinates = self.find_all_templates(hsv_sc, hsv_template)
        matched_coordinates = self.find_all_templates(screenshot, template)
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

    def run_ads(self):
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


class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        print(f"{self.name} elapsed time: {elapsed_time} seconds\n")


close_nofication_coords = {
    'x': 710,
    'y': 1894
}

first_lemonade_stand_open_coords = {
    'x': 713,
    'y': 1845
}

settings_coords = {
    'x': 1339,
    'y': 185
}

cloud_save_coords = {
    'x': 654,
    'y': 1632
}

email_input_coords = {
    'x': 700,
    'y': 1320
}

password_input_coords = {
    'x': 700,
    'y': 1600,
}

text_ok_button_coords = {
    'x': 1374,
    'y': 1845,
}

login_button_coords = {
    'x': 700,
    'y': 1940
}

use_cloud_save_button_coords = {
    'x': 990,
    'y': 2100
}

close_game_for_restart_button_coords = {
    'x': 734,
    'y': 1821
}

close_offline_earnings_coords = {
    'x': 1150,
    'y': 1164
}

upgrade_button_coords = {
    'x': 1290,
    'y': 2904
}

single_upgrade_button_coords = {
    'x': 1143,
    'y': 1283
}

close_upgrade_button_coords = {
    'x': 1222,
    'y': 1045
}

next_level_button_coords = {
    'x': 150,
    'y': 2900
}

renovate_button_coords = {
    'x': 700,
    'y': 2200
}

ads_button_coords = {
    'x': 720,
    'y': 2950
}


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

# below logic is after setup is done and you start the game regulartly
while True:
    dev.capture_screenshot()
    if dev.is_having_settings():
        break
    if dev.is_having_offline_earnings():
        dev.click(close_offline_earnings_coords)
        break

    time.sleep(5)


# upgrade click
# time.sleep(2)
# dev.click(upgrade_button_coords)
# time.sleep(1)
# while True:
#     dev.capture_screenshot()
#     if dev.is_having_single_upgrade():
#         dev.click(single_upgrade_button_coords)
#     else:
#         dev.click(close_upgrade_button_coords)
#         break
#     time.sleep(0.5)

# boxes find and click
# dev.capture_screenshot()
# if dev.is_having_box():
#     coords = dev.get_all_boxes_locations()
#     for c in coords:
#         dev.click(c)
#         time.sleep(0.5)


# get better updates
count = 0
start_time = time.time()
while True:
    count += 1

    # check for ads
    if count == 1 or count % 100 == 0:  # every 100th iteration
        with Timer("Running ads"):
            print('Checking for boost')
            if dev.is_having_no_boost_indicator_2x():
                print('running ads')
                dev.run_ads()
                time.sleep(2)

    with Timer("Capturing screenshot"):
        dev.capture_screenshot()

    # maind upgrades
    # upgrade click
    if count % 5 == 0:
        with Timer("Upgrading items"):
            print('Upgrading items')
            dev.click(upgrade_button_coords)
            time.sleep(0.3)
            for i in range(5):
                dev.click(single_upgrade_button_coords)
                time.sleep(0.2)
            dev.click(close_upgrade_button_coords)
            dev.capture_screenshot()

    if count % 2 == 0:
        with Timer("Finding boxes"):
            # boxes find and click
            print('finding boxes')
            coords = dev.get_all_boxes_locations()
            for c in coords:
                dev.click(c)
                time.sleep(0.2)

    with Timer("Finding food icons"):
        # dev.capture_screenshot()
        print('finding food icons')
        coords = dev.get_all_better_food_icon_locations()
    if len(coords) != 0:
        # c = random.choice(coords)
        with Timer("Clicking food icons"):
            random.shuffle(coords)
            for c in coords[:3]: # as mostly after 3 no food icon is visible
                dev.click(c)
                time.sleep(0.1)

                # hack for better food button
                y_neg_offset = 150
                dev.click_and_hold(c[0], c[1] - y_neg_offset, 700)
                time.sleep(0.1)
                dev.click([c[0], c[1] + 30])
                time.sleep(0.1)
    else:
        # next level check
        print('next level check')
        if dev.is_having_next_level_icon():
            dev.click(next_level_button_coords)
            time.sleep(0.2)
            dev.click(renovate_button_coords)
            time.sleep(10)
            dev.click(first_lemonade_stand_open_coords)

# collect full boost
# time.sleep(2)
# for i in range(12):
#     dev.run_ads()


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
