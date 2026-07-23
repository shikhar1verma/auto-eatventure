from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
import time
from scaled_coords import ScaledCoords, detect_resolution_appium

desired_cap = {
  "platformName": "Android",
  "appium:deviceName": "Android Emulator",
  "appium:appPackage": "com.hwqgrhhjfd.idlefastfood",
  "appium:appActivity": "com.unity3d.player.UnityPlayerActivity"
}

driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_cap)

# deny notifiication
driver.implicitly_wait(60)
driver.find_element(MobileBy.ID, "com.android.permissioncontroller:id/permission_deny_button").click()

# start screen
time.sleep(3)
actual_w, actual_h = detect_resolution_appium(driver)
sc = ScaledCoords(actual_w, actual_h)
action = TouchAction(driver)
x = sc.initial_tap_x
y = sc.initial_tap_y
action.tap(x=x, y=y).perform()
