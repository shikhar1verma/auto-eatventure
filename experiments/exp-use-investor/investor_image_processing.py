import cv2
import time
import numpy as np



def create_mask_rgb(image, lower_color, upper_color):
    lower_bound = np.array(lower_color, dtype=np.uint8)
    upper_bound = np.array(upper_color, dtype=np.uint8)
    return cv2.inRange(image, lower_bound, upper_bound)

def load_image_in_bgr(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not load the image: {image_path}")

    # Check the number of channels
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Assuming the image is in RGB format, convert it to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image

# RGB
# hat = [(127, 119, 77)]
# face = [(254, 221, 131), (255, 215, 129), (254, 225, 133)]
# body = [(173, 163, 92)]
# bag = [(198, 216, 241)]

bag_color = [(198, 214, 241)]
hat_eye_cloth_colors = [(131, 122, 77), (104, 100, 72), (146, 138, 83), (180, 171, 97), (158, 149, 86), (169, 159, 90)]
skin_color = [(254, 217, 129), (254, 222, 131), (254, 224, 132)]
bag_handle_color = [(196, 224, 255), (204, 228, 254), (202, 233, 255)]

image = cv2.imread("./image.png")
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

tolerance = 13

# hat_mask = create_mask_rgb(rgb_image, [hat[0][0] - tolerance, hat[0][1] - tolerance, hat[0][2] - tolerance], [hat[0][0] + tolerance, hat[0][1] + tolerance, hat[0][2] + tolerance])
hat_mask = create_mask_rgb(rgb_image, [bag_color[0][0] - tolerance, bag_color[0][1] - tolerance, bag_color[0][2] - tolerance], [bag_color[0][0] + tolerance, bag_color[0][1] + tolerance, bag_color[0][2] + tolerance])

mask_list = []
# for color in face + bag+ body:
for color in hat_eye_cloth_colors + skin_color + bag_handle_color:
    mask = create_mask_rgb(rgb_image, [color[0] - tolerance, color[1] - tolerance, color[2] - tolerance], [color[0] + tolerance, color[1] + tolerance, color[2] + tolerance])
    mask_list.append(mask)

combined_mask = hat_mask
for mask in mask_list:
    combined_mask = cv2.bitwise_or(combined_mask, mask)

# investor = cv2.imread('./template3.png')
result = cv2.bitwise_and(rgb_image, rgb_image, mask=combined_mask)

cv2.imwrite("./original.png", image)
cv2.imwrite("./original_rgb.png", rgb_image)
cv2.imwrite("./original_converted_result.png", result)