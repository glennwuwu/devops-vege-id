import time
import os
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from faker import Faker

# Configure Chrome WebDriver with options
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Replace with your Selenium server URL and port
driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    options=options,
)

base_url = "https://bonk-choy.onrender.com"


fake = Faker()


username = fake.user_name() + "_rpa_user"
password = fake.password()


class_keys = {
    "Bean": 0,
    "Bitter Gourd": 1,
    "Bottle Gourd": 2,
    "Brinjal": 3,
    "Broccoli": 4,
    "Cabbage": 5,
    "Capsicum": 6,
    "Carrot": 7,
    "Cauliflower": 8,
    "Cucumber": 9,
    "Papaya": 10,
    "Potato": 11,
    "Pumpkin": 12,
    "Radish": 13,
    "Tomato": 14,
}


def check_sign_in_verification():
    print("Checking unauthorised accesses: ", end="")
    try:
        driver.get(base_url + "/upload")
        assert driver.current_url.split(base_url)[1] == "/user/sign_in"
        driver.get(base_url + "/history")
        assert driver.current_url.split(base_url)[1] == "/user/sign_in"
        driver.get(base_url + "/prediction")
        assert driver.current_url.split(base_url)[1] == "/user/sign_in"

        print("Success")
        return True
    except Exception as e:
        print(e)
        return False


def create_account(username, password):
    print("Creating account: ", end="")
    try:
        button_text = "Upload Image"
        xpath = f"//div[text()='{button_text}']/ancestor::a"
        element = driver.find_element(By.XPATH, xpath)
        element.click()

        assert driver.current_url.split(base_url)[1] == "/user/sign_in"

        link_text = "Create new account"
        link = driver.find_element(By.LINK_TEXT, link_text)
        link.click()

        assert driver.current_url.split(base_url)[1] == "/user/sign_up"

        # Generate a random username using Faker

        key_in_details(username, password)
        assert driver.current_url.split(base_url)[1] == "/user/sign_in"

        key_in_details(username, password)
        assert driver.current_url.split(base_url)[1] == "/upload"

        print("Success")
        return True
    except Exception as e:
        print(e)
        return False


# Input the generated username into the field
def key_in_details(username, password):
    input_element = driver.find_element(By.ID, "username")
    input_element.send_keys(username)

    input_element = driver.find_element(By.ID, "password")
    input_element.send_keys(password)

    submit = driver.find_element(By.ID, "submit")
    submit.click()


def upload_image(model):
    print(f"Uploading an image, model size: {model}", end="")
    try:
        driver.get(base_url + "/upload")
        file_input = driver.find_element(By.ID, "fileUpload")
        file_path = os.getcwd() + "/tests/assets/images/0017.jpg"
        file_input.send_keys(file_path)

        driver.implicitly_wait(2)

        model_select = driver.find_element(By.ID, "model")
        select = Select(model_select)
        select.select_by_visible_text(model)
        submit = driver.find_element(By.ID, "submitButton")
        submit.click()

        redirect_substring = "/prediction"
        WebDriverWait(driver, 10).until(EC.url_contains(redirect_substring))

        prediction_url = driver.current_url.split(base_url)[1]
        assert "/prediction" in prediction_url

        image_id = prediction_url.split("image_id=")[1]
        print("")
        return True, image_id
    except Exception as e:
        print(e)
        return False, -1


def try_click_next_page(curr_page):
    try:
        # Click on the "Next Page" link
        next_page_link = driver.find_element(
            By.XPATH, f'//a[@href="/history?page={curr_page+1}&label="]'
        )
        next_page_link.click()
        print("Next Page link found.")
        return True
    except NoSuchElementException:
        print("Next Page link not found. Exiting...")
        return False


def delete_history(image_id):
    try:
        while True:
            curr_page = 1
            try:
                driver.get(base_url + "/history")
                delete_button = driver.find_element(
                    By.XPATH,
                    f'//tr[.//span[text()="{image_id}"]]//button[contains(., "Delete")]',
                )

                delete_button.click()
                print(f"Image with ID {image_id} deleted")
                return True
            except NoSuchElementException:
                # Handle the case where the delete button is not found
                print(f"Delete button not found for image ID {image_id}")
                if not try_click_next_page(curr_page):
                    return False
                curr_page += 1

    except Exception as e:
        print(e)
        return False


def filter_history_model(model, n_entries):
    print(f"Filtering prediction entries by model {model}: ")
    try:
        driver.get(base_url + "/history")
        model_select = driver.find_element(By.ID, "model")
        select = Select(model_select)
        select.select_by_visible_text(model)
        submit = driver.find_element(By.ID, "sort")
        submit.click()

        all_rows = []

        while True:
            curr_page = 1

            rows = driver.find_elements(
                By.ID,
                "prediction_model",
            )

            all_rows += [row.text for row in rows]

            if not try_click_next_page(curr_page):
                break
            curr_page += 1

        for text in all_rows:
            if model != "*":
                assert text == model

        assert len(all_rows) == n_entries

        print("Success")
    except Exception as e:
        print(e)
        return False


def sort_history_date(date_oldest_first):
    if date_oldest_first:
        order = "Ascending (Oldest first)"
    else:
        order = "Descending (Latest first)"
    print(f"Sorting prediction entries by date {order}: ")
    try:
        driver.get(base_url + "/history")
        date_select = driver.find_element(By.ID, "date_oldest_first")
        select = Select(date_select)
        select.select_by_visible_text(order)
        submit = driver.find_element(By.ID, "sort")
        submit.click()
        all_rows = []

        while True:
            curr_page = 1

            rows = driver.find_elements(
                By.ID,
                "prediction_id",
            )

            all_rows += [row.text for row in rows]

            if not try_click_next_page(curr_page):
                break
            curr_page += 1

        if date_oldest_first:
            prev_int = -1
        else:
            prev_int = math.inf

        for text in all_rows:
            curr_int = int(text)
            if date_oldest_first:
                assert prev_int < curr_int
            else:
                assert prev_int > curr_int
            prev_int = curr_int

        print("Success")
    except Exception as e:
        print(e)
        return False


def search_history_label(label):
    print(f"Filtering prediction entries by label {label}: ")
    try:
        driver.get(base_url + "/history")
        input_element = driver.find_element(By.ID, "label")
        input_element.clear()
        input_element.send_keys(label)
        input_element.send_keys(Keys.RETURN)

        all_rows = []

        while True:
            curr_page = 1

            rows = driver.find_elements(
                By.ID,
                "prediction_label",
            )

            all_rows += [row.text for row in rows]

            if not try_click_next_page(curr_page):
                break
            curr_page += 1

        for text in all_rows:
            assert text == label

        print("Success")
    except Exception as e:
        print(e)
        return False


def click_sign_out():
    print("Signing out: ", end="")
    try:
        sign_out_link = driver.find_element(By.XPATH, '//a[@href="/user/sign_out"]')
        sign_out_link.click()
        print("Success")
        return True

    except Exception as e:
        print(e)
        return False


try:
    # Navigate to your site
    driver.get(base_url)

    check_sign_in_verification()

    create_account(username, password)

    image_ids = [upload_image("Small")[1], upload_image("Large")[1]]
    print(image_ids)

    filter_history_model("Small", 1)
    filter_history_model("Large", 1)
    filter_history_model("*", 2)

    sort_history_date(True)
    sort_history_date(False)

    for label in list(class_keys.keys()):
        search_history_label(label)

    for image_id in image_ids:
        delete_history(image_id)

    # TODO
    # History page: go to prediction details page

    click_sign_out()

    check_sign_in_verification()

except Exception as e:
    print(e)

finally:
    # Close the WebDriver session
    driver.quit()
