"""Main application."""

# Core Libs
import time
import logging

# Third Party Libs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)
from typer import Typer, Option, Argument

app = Typer()


def _resume_level(driver, url_root: str):
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
        driver.get(f"{url_root.rstrip('/')}dash/index")


@app.command()
def run(
    url: str = Argument(
        ...,
        help="URL to the video. Ex. https://app.aarpdriversafety.org/courseflow/page/9B3gwbKQ7Xalh2Vk",
    ),
    email: str = Argument(..., help="Email to login with."),
    password: str = Argument(..., help="Password to login with."),
    option_url_root: str = Option(
        "https://app.aarpdriversafety.org/", "--url-root", help="URL root."
    ),
    chrome_browser_binary: str = Option(
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        help=(
            "Path to the browser binary. "
            "Another example may be `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`"
        ),
    ),
    chrome_driver_binary: str = Option(
        "/usr/local/bin/chromedriver", help="Path to the driver binary."
    ),
):
    """Run the bot."""

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_browser_binary
    driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

    driver.get(url)

    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("user-signin-submit").click()
    time.sleep(7)

    _resume_level(driver=driver, url_root=option_url_root)

    count_failure_page_arrow_find = 0
    while True:
        list_elements_continue = driver.find_elements_by_xpath(
            r'//span[text()="Continue"]'
        )
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
                _resume_level(driver=driver, url_root=option_url_root)

        list_elements_play = driver.find_elements_by_class_name("vjs-big-play-button")
        if len(list_elements_play):
            logging.info("Found play button, playing video.")

            try:
                list_elements_play[0].click()
            except ElementNotInteractableException:
                logging.warning(
                    "Tried to play video, but could not, reattempting page."
                )
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


if __name__ == "__main__":
    app()
