import logging.config
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

username = ""
password = ""
url = "https://www.nike.com/t/kd13-play-for-the-future-basketball-shoe-NVWhwJ/CW3159-001"
shoe_size = ""

NIKE_LOGIN_URL = "https://www.nike.com/login"
SUBMIT_BUTTON_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div[6]/button"
LOGGER = logging.getLogger()

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [PID %(process)d] [Thread %(thread)d] [%(levelname)s] [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})


def login(driver, username, password):
    try:
        LOGGER.info("Requesting page: " + NIKE_LOGIN_URL)
        driver.get(NIKE_LOGIN_URL)
    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    LOGGER.info("Entering username and password")
    email_input = driver.find_element_by_xpath("//input[@name='emailAddress']")
    email_input.clear()
    email_input.send_keys(username)

    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.clear()
    password_input.send_keys(password)

    LOGGER.info("Logging in")
    driver.find_element_by_xpath("//input[@value='SIGN IN']").click()

    LOGGER.info("Successfully logged in")


def select_shoe_size(driver, shoe_size):
    LOGGER.info("Waiting for size dropdown to appear")
    LOGGER.info("Selecting size from dropdown")
    # driver.find_element_by_xpath("//fieldset/div/div[5]").click()
    driver.find_element_by_xpath(f"//*[text()[contains(.,'{shoe_size}')]]").click()


def click_buy_button(driver):
    xpath = "//button[@aria-label='Add to Bag']"

    LOGGER.info("Clicking buy button")
    driver.find_element_by_xpath(xpath).click()
    LOGGER.info("Added to cart")

def automating(driver, username, password, url, shoe_size):
    driver.maximize_window()
    try:
        login(driver=driver, username=username, password=password)
        print("login successful")

        try:
            LOGGER.info("Requesting page: " + url)
            driver.get(url)
            print("Url successfully reached")

        except TimeoutException:
            LOGGER.info("Page load timed out but continuing anyway")

        try:
            select_shoe_size(driver, shoe_size=shoe_size)
            print(f"shoe size selected: {shoe_size}")

        except Exception as e:
            # Try refreshing page since you can't click Buy button without selecting size (except if size parameter passed in)
            LOGGER.exception("Failed to select shoe size: " + str(e))

        try:
            click_buy_button(driver=driver)
        except Exception as e:
            LOGGER.exception("Failed to click buy button: " + str(e))

    except TimeoutException:
        LOGGER.info("Failed to login due to timeout. Retrying...")
    except Exception as e:
        LOGGER.exception("Failed to login: " + str(e))


if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if "win32" in sys.platform:
        executable_path = "./bin/chromedriver_win32.exe"
    else:
        raise Exception(
            "Drivers for installed operating system not found. Try specifying the path to the drivers with the --webdriver-path option")
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    print(driver.execute_script("return navigator.userAgent;"))

    automating(driver, username, password, url, shoe_size)