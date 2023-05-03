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
        # result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        # locations = np.where(result >= threshold)
        # mask = np.zeros_like(result, dtype=np.uint8)
        # mask[locations] = 255

        # # Find connected components in the binary mask
        # num_labels, _, stats, _ = cv2.connectedComponentsWithStats(
        #     mask, connectivity=8)

        # # Convert the stats to a list of rectangles
        # centers = []
        # for i in range(1, num_labels):
        #     x, y, w, h, _ = stats[i]
        #     # center_x = x + w // 2
        #     # center_x = x
        #     center_x = x + w
        #     # center_y = y + h // 2
        #     # center_y = y
        #     center_y = y + h
        #     centers.append((center_x, center_y))

        # return centers
        template_width, template_height = template.shape[::-1]
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
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

    def is_image_template_matching(self, matching_img_path):
        screenshot = cv2.imread(self.captured_sc_path)
        template = cv2.imread(matching_img_path)
        hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        matched_coordinates = self.find_template(hsv_sc, hsv_template)
        if matched_coordinates:
            return True
        return False

    def is_having_notification(self):
        return self.is_image_template_matching(self.matching_screenshots_path['notification'])

    def is_having_first_lemonade_stand_open(self):
        return self.is_image_template_matching(self.matching_screenshots_path['first_lemondae_stand_open'])

    def is_having_settings(self):
        return self.is_image_template_matching(self.matching_screenshots_path['settings'])

    def is_having_offline_earnings(self):
        return self.is_image_template_matching(self.matching_screenshots_path['offline_earnings'])

    def is_having_upgrade(self):
        return self.is_image_template_matching(self.matching_screenshots_path['upgrade_button'])

    def is_having_single_upgrade(self):
        return self.is_image_template_matching(self.matching_screenshots_path['single_upgrade'])

    def is_having_box(self):
        return self.is_image_template_matching(self.matching_screenshots_path['box'])

    def is_having_better_food_icon(self):
        return self.is_image_template_matching(self.matching_screenshots_path['buy_better_food_icon'])

    def is_having_better_food_button(self):
        return self.is_image_template_matching(self.matching_screenshots_path['buy_better_food_button'])

    def get_all_boxes_locations(self):
        screenshot = cv2.imread(self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(
            self.matching_screenshots_path['box'], cv2.IMREAD_GRAYSCALE)
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # matched_coordinates = self.find_all_templates(hsv_sc, hsv_template)
        matched_coordinates = self.find_all_templates(screenshot, template)
        return matched_coordinates

    def get_all_better_food_icon_locations(self):
        screenshot = cv2.imread(self.captured_sc_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(
            self.matching_screenshots_path['buy_better_food_icon'], cv2.IMREAD_GRAYSCALE)
        # hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # matched_coordinates = self.find_all_templates(hsv_sc, hsv_template)
        matched_coordinates = self.find_all_templates(
            screenshot, template, end=True)
        return matched_coordinates

    def get_better_food_button(self):
        screenshot = cv2.imread(self.captured_sc_path)
        template = cv2.imread(
            self.matching_screenshots_path['buy_better_food_button'])
        hsv_sc = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        matched_coordinates = self.find_template(hsv_sc, hsv_template)
        return matched_coordinates

    def click(self, coords):
        if type(coords) is dict:
            self.device.shell(f"input tap {coords['x']} {coords['y']}")
        if type(coords) is list:
            self.device.shell(f"input tap {coords[0]} {coords[1]}")
        return

    def click_and_hold(self, x, y, hold_duration=5):
        self.device.shell(
            f'input swipe {x} {y} {x} {y} {hold_duration * 1000}')
        return

    def input_text(self, text):
        # Escape special characters and spaces
        escaped_text = text.replace(" ", "%s").replace(
            "&", "\\&").replace("|", "\\|")
        self.device.shell(f"input text '{escaped_text}'")
        return


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
dev.capture_screenshot()
if dev.is_having_better_food_icon():
    while True:
        dev.capture_screenshot()
        # maind upgrades
        # upgrade click
        if dev.is_having_upgrade():
            dev.click(upgrade_button_coords)
            time.sleep(0.3)
            while True:
                dev.capture_screenshot()
                if dev.is_having_single_upgrade():
                    dev.click(single_upgrade_button_coords)
                else:
                    dev.click(close_upgrade_button_coords)
                    break
                time.sleep(0.2)

        dev.capture_screenshot()
        # boxes find and click
        if dev.is_having_box():
            print('finding boxes')
            coords = dev.get_all_boxes_locations()
            for c in coords:
                dev.click(c)
                time.sleep(0.2)
            print()

        dev.capture_screenshot()
        print('finding food icons')
        coords = dev.get_all_better_food_icon_locations()
        if len(coords) == 0:
            time.sleep(5)
            continue

        c = random.choice(coords)
        dev.click(c)
        print()
        time.sleep(0.1)
        # dev.capture_screenshot()
        # print('finding better food button')
        # bt_c = dev.get_better_food_button()
        # if bt_c:
            # dev.click_and_hold(bt_c[0], bt_c[1], 3)
        
        # hack for better food button
        y_neg_offset = 150
        dev.click_and_hold(c[0], c[1] - y_neg_offset, 3)

        time.sleep(0.1)


# for annotating points
# print(len(coords))
# print('coords', coords)
# sc = cv2.imread(dev.captured_sc_path)
# for c in coords:
#     cv2.circle(sc, (c[0], c[1]), radius=10,
#                 color=(0, 0, 255), thickness=-1)
# cv2.imwrite('./captured_screenshots_on_the_fly/annotated_screenshot.png', sc)
