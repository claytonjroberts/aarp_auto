"""<button class="vjs-big-play-button" type="button" title="Play Video" aria-disabled="false"><span aria-hidden="true" class="vjs-icon-placeholder"></span><span class="vjs-control-text" aria-live="polite">Play Video</span></button>"""

import time
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)

options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
chrome_driver_binary = "/usr/local/bin/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

driver.get("https://app.aarpdriversafety.org/courseflow/page/9B3gwbKQ7Xalh2Vk")

driver.find_element_by_id("email").send_keys("claytonjroberts@icloud.com")
driver.find_element_by_id("password").send_keys("leap7clum*DOOT0kouf")
driver.find_element_by_id("user-signin-submit").click()
time.sleep(7)


def resume_level():
    while True:
        for text in ["Resume level", "Start level"]:
            try:
                driver.find_elements_by_xpath(rf'//div[text()="{text}"]')[0].click()
                return
            except (
                ElementClickInterceptedException,
                ElementNotInteractableException,
                IndexError,
            ):
                pass

        time.sleep(3)
        driver.get("https://app.aarpdriversafety.org/dash/index")


resume_level()

count_failure_page_arrow_find = 0
while True:

    list_elements_continue = driver.find_elements_by_xpath(r'//span[text()="Continue"]')
    if len(list_elements_continue):
        try:
            list_elements_continue[0].click()
        except ElementNotInteractableException:
            logging.warning(
                "Tried to click continue, but could not, reattempting page."
            )
            time.sleep(1)
            continue
        else:
            resume_level()

    list_elements_play = driver.find_elements_by_class_name("vjs-big-play-button")
    if len(list_elements_play):
        logging.info("Found play button, playing video.")

        try:
            list_elements_play[0].click()
        except ElementNotInteractableException:
            logging.warning("Tried to play video, but could not, reattempting page.")
            time.sleep(1)
            continue

    try:
        elem_next = driver.find_element_by_id("arrow-next")
    except NoSuchElementException:
        if count_failure_page_arrow_find > 10:
            raise

        logging.warning("Tried to play video, but could not, reattempting page.")
        count_failure_page_arrow_find += 1
        time.sleep(1)
        continue

    while True:
        try:
            elem_next.click()
        except ElementNotInteractableException:
            time.sleep(5)
        except StaleElementReferenceException:
            break
        else:
            count_failure_page_arrow_find = 0

            logging.info("Successfully progressed.")
            break

driver.close()
