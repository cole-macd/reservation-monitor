import config
from sms import SMS

import sys
import time
import traceback

from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


def book_day(day_el, driver):
    driver.execute_script("arguments[0].click();", day_el)

    passholder_checkbox_xpath = "//div[contains(@class, 'shared_modal__container')]//input[@type='checkbox']"
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, passholder_checkbox_xpath)))
    driver.find_element_by_xpath(passholder_checkbox_xpath).click()
    assign_button_xpath = "//div[contains(@class, 'shared_modal__container')]//button[text()='Assign Pass Holders']"
    WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, assign_button_xpath)))
    driver.find_element_by_xpath(assign_button_xpath).click()

    try:
        already_reserved_xpath = "//h4[@class='passholder_reservations__assign_passholder_modal__error error']"
        WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, already_reserved_xpath)))
        print("Already booked date")
        return True
    except TimeoutException:
        pass

    terms_accepted_id = "terms-accepted"
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, terms_accepted_id)))
    terms_accepted_checkbox = driver.find_element_by_id(terms_accepted_id)
    driver.execute_script("arguments[0].click();", terms_accepted_checkbox)

    complete_res_xpath = "//div[@class='passholder_reservations__completion__cta']/button"
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, complete_res_xpath)))
    complete_res_button = driver.find_element_by_xpath(complete_res_xpath)
    return True
    driver.execute_script("arguments[0].click();", complete_res_button)
    time.sleep(1)
    try:
        reservation_error_xpath = "//h4[@class='error pending_reservation__error']"
        driver.find_element_by_xpath(reservation_error_xpath)
    except NoSuchElementException:
        return False
    return True


def check_reservations(driver, months, days, times_checked):
    try:
        # Go to reservations and pull up whistler
        reservations_page = "https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx"
        driver.get(reservations_page)

        resort_selector_id = "PassHolderReservationComponent_Resort_Selection"
        whistler_selector_value = '80'
        check_availability_button_id = "passHolderReservationsSearchButton"

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, resort_selector_id)))
        select = Select(driver.find_element_by_id(resort_selector_id))
        select.select_by_value(whistler_selector_value)
        WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, check_availability_button_id)))
        check_availability_button = driver.find_element_by_id(check_availability_button_id)
        driver.execute_script("arguments[0].click();", check_availability_button)

        # Get correct month
        # TODO

        # Check for days
        calendar_div_xpath = "//div[@class='passholder_reservations__calendar__days']"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, calendar_div_xpath)))
        time.sleep(1)
        calendar_el = driver.find_element_by_xpath(calendar_div_xpath)
        day_els = calendar_el.find_elements_by_tag_name("button")

        for day_el in day_els:
            if not day_el.get_attribute('disabled'):
                if day_el.text in days:
                    print("Times Checked: %s" % times_checked)
                    print("%s %s is now available!" % (month, day_el.text))
                    print("Found result at %s" % datetime.now().time())
                    if book_day(day_el, driver):
                        sms = SMS(config.phone_number, config.phone_carrier,
                                config.email_address, config.email_password)
                        sms.send("%s %s was attempted to be booked at Whistler Blackcomb.\n" \
                                "Please look for a confirmation email shortly." % (
                                month, day_el.text), "Reservation Found")
                        sys.exit()
                    else:
                        print("Error booking day")

        print("Times Checked: %s" % times_checked, end='\r')
    except TimeoutException:
        traceback.print_exc()
        print("Will try again...")
    finally:
        time.sleep(config.refresh_frequency_seconds)


def login(driver):
    action = ActionChains(driver)
    login_xpath = "//li[@class='main_nav__utility_item hidden-md hidden-sm hidden-xs']"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, login_xpath)))
    login_el = driver.find_element_by_xpath(login_xpath)
    action.move_to_element(login_el).perform()

    username_id = "txtUserName_1"
    password_id = "txtPassword_1"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, username_id)))
    driver.find_element_by_id(username_id).send_keys(config.epic_username)
    driver.find_element_by_id(password_id).send_keys(config.epic_password)

    sign_in_button_xpath = "//button[@class='btn primaryCTA primaryCTA--full accountLogin__cta']"
    driver.find_element_by_xpath(sign_in_button_xpath).click()

    logged_in_xpath = "//a[@class='main_nav__account_state-hot loggedin']"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, logged_in_xpath)))
    print("Logged In")



# Input is in form of Month [Day]
if len(sys.argv) < 3:
    print("Inputs are in the form of: Month [Day]")
    sys.exit()
month = sys.argv[1]
days = sys.argv[2:]
print("Searching for reservations in %s on days %s" % (month, days))
print("Began searching at %s" % datetime.now().time())

window_size = "--window-size=1920,1200"
homepage = "https://www.epicpass.com/"
options = Options()
#options.headless = True
options.add_argument(window_size)
driver = webdriver.Chrome(options=options)
driver.get(homepage)

login(driver)
times_checked = 0;

while True:
    times_checked += 1;
    check_reservations(driver, month, days, times_checked)

