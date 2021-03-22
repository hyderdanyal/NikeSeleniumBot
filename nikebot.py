import logging.config
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from main import wait_until_present

username = ""
password = ""
url = "https://www.nike.com/t/kd13-play-for-the-future-basketball-shoe-NVWhwJ/CW3159-001"
shoe_size = "M 10"

NIKE_LOGIN_URL = "https://www.nike.com/login"
NIKE_CART_URL = "https://www.nike.com/cart"
NIKE_CHECKOUT_URL = "https://www.nike.com/checkout/tunnel"
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


def click_guest_checkout(driver):
    xpath = "//button[@aria-label='Guest Checkout']"

    LOGGER.info("Clicking guest checkout button")
    driver.find_element_by_xpath(xpath).click()

    LOGGER.info("Guest checked out")


def click_signin_button(driver):
    driver.find_element_by_xpath("//button[@data-path='sign in']").click()

    LOGGER.info("Waiting for login fields to become visible")
    wait_until_visible(driver=driver, xpath="//input[@placeholder='Email address']")

    LOGGER.info("Entering username and password")
    email_input = driver.find_element_by_xpath("//input[@placeholder='Email address']")
    email_input.clear()
    email_input.send_keys(username)

    password_input = driver.find_element_by_xpath("//input[@placeholder='Password']")
    password_input.clear()
    password_input.send_keys(password)

    LOGGER.info("Logging in")
    driver.find_element_by_xpath("//input[@value='SIGN IN']").click()

    LOGGER.info("Successfully logged in")


def wait_until_visible(driver, xpath, duration=10000, frequency=0.1):
    WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))


def login(driver, username, password):
    try:
        LOGGER.info("Requesting page: " + NIKE_LOGIN_URL)
        driver.get(NIKE_LOGIN_URL)

    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    LOGGER.info("Waiting for login fields to become visible")
    wait_until_visible(driver=driver, xpath="//input[@name='emailAddress']")

    # LOGGER.info("Deleting cookies")
    # driver.delete_all_cookies()

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

    LOGGER.info("Waiting for buy button to become present")
    # element = wait_until_present(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking buy button")
    driver.execute_script("window.scrollTo(0, 1080)")
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

        # try:
        #     LOGGER.info("Requesting cart: " + NIKE_CART_URL)
        #     driver.get(NIKE_CART_URL)
        #
        # except TimeoutException:
        #     LOGGER.info("CART load timed out")

        # try:
        #     LOGGER.info("Trying signing in using button :")
        #     click_signin_button(driver=driver)
        # except Exception as e:
        #     LOGGER.exception("Failed to click sign in button: " + str(e))


        try:
            LOGGER.info("Requesting checkout tunnel: " + NIKE_CHECKOUT_URL)
            driver.get(NIKE_CHECKOUT_URL)
            click_guest_checkout(driver)

        except TimeoutException:
            LOGGER.info("CHECKOUT TUNNEL load timed out")





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
