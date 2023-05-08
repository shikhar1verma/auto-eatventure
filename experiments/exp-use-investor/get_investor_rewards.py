import cv2
from adbutils import adb
import time
import numpy as np
import io
import subprocess
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


def find_template(image, template, threshold=0.8):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    matches = cv2.minMaxLoc(result)
    print(matches)
    _, max_val, _, max_loc = matches

    if max_val > threshold:
        return max_loc
    return None


def get_screenshot(device):
    adb_command = f'adb -s {device.serial} shell screencap -p'
    output = subprocess.check_output(adb_command.split())

    # Convert the output to a PIL Image object
    pilimg = Image.open(io.BytesIO(output))
    pilimg.load()
    pilimg = pilimg.convert("RGB")

    # # Convert PIL image to numpy array (OpenCV format)
    open_cv_image = np.array(pilimg)
    open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR

    return open_cv_image


def load_image_in_bgr(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not load the image: {image_path}")

    # Check the number of channels
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Assuming the image is in RGB format, convert it to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


def apply_investor_mask(image, tolerance=15):
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


package_name = "com.hwqgrhhjfd.idlefastfood"
device = adb.device()

claim_button_coords = {
    'x': 720,
    'y': 2020
}

# time.sleep(1)
# im_gray = cv2.imread("./image.png", cv2.IMREAD_GRAYSCALE)
# im_bw_image = cv2.threshold(im_gray, 150, 255, cv2.THRESH_BINARY)[1]
# cv2.imwrite("./image_bw.png", im_bw_image)

# im_gray = cv2.imread("./template.png", cv2.IMREAD_GRAYSCALE)
# im_bw_template = cv2.threshold(im_gray, 150, 255, cv2.THRESH_BINARY)[1]
# cv2.imwrite("./template_bw.png", im_bw_template)

# template = cv2.imread("./template2.png", cv2.IMREAD_GRAYSCALE)

hat = (127, 119, 77)
face = (254, 221, 131)
bag = (198, 216, 241)

# threshold = 90
template = cv2.imread("./template4.png")
template = apply_investor_mask(template)
# cv2.imwrite("./investor_mask.png", template)

# image1 = cv2.imread("./image.png")
# image1 = apply_investor_mask(image1)
# cv2.imwrite("./image1_investor_mask.png", image1)

# image2 = cv2.imread("./image2.png")
# image2 = apply_investor_mask(image2)
# cv2.imwrite("./image2_investor_mask.png", image2)

# find_template(image1, template)
# find_template(image2, template)

# image = load_image_in_bgr('./image.png')
# cv2.imwrite('./image_investor_mask.png', image)
# image = apply_investor_mask(image)

# bag_color = #c6d6f1 |
# hat_color = #837a4d | #686448 | #686448
# eye_color = #928a53
# cloth_color = #928a53 | #b4ab61 | #9e9556
# skin_color = #fed981 | #fede83 | #fee084


while True:
    sc = get_screenshot(device)
    sc = apply_investor_mask(sc)
    match = find_template(sc, template)
    if match:
      print('Match found now clicking')
      device.shell(f"input tap {match[0] + 20} {match[1] + 20}")
      time.sleep(1)
      print('Now claiming')
      device.shell(f"input tap 720 2020")
      time.sleep(5)
      device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
      time.sleep(2)

    time.sleep(3)
