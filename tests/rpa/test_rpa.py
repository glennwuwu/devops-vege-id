import time
import os
import math

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from faker import Faker


UPLOAD_IMAGES_SMALL_COUNT = 12
UPLOAD_IMAGES_LARGE_COUNT = 12
TOTAL_UPLOAD_IMAGES_COUNT = UPLOAD_IMAGES_SMALL_COUNT + UPLOAD_IMAGES_LARGE_COUNT


@pytest.fixture
@pytest.mark.rpa
def driver(loc, browser):
    executor = {
        "local": "http://localhost:4444/wd/hub",
        "CI": f"http://selenium__standalone-{browser}:4444/wd/hub",
    }

    if browser == "chrome":
        options = webdriver.ChromeOptions()
    elif browser == "edge":
        options = webdriver.EdgeOptions()
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")

    # Replace with your Selenium server URL and port
    _driver = webdriver.Remote(
        command_executor=executor[loc],
        options=options,
    )
    yield _driver

    _driver.quit()


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


@pytest.mark.rpa
def test_sign_in_verification(driver):
    driver.get(base_url)

    check_sign_in_verification(driver)


@pytest.mark.rpa
def test_create_account(driver):
    driver.get(base_url)

    create_account(driver, username, password)


@pytest.mark.rpa
@pytest.mark.parametrize(
    "count, model",
    [[UPLOAD_IMAGES_LARGE_COUNT, "Large"], [UPLOAD_IMAGES_SMALL_COUNT, "Small"]],
)
def test_upload_image(driver, count, model):
    driver.get(base_url)

    create_account(driver, username, password)

    for _ in range(count):
        pytest.rpa_image_ids.append(upload_image(driver, model))


@pytest.mark.rpa
@pytest.mark.parametrize(
    "count, model",
    [
        [UPLOAD_IMAGES_LARGE_COUNT, "Large"],
        [UPLOAD_IMAGES_SMALL_COUNT, "Small"],
        [TOTAL_UPLOAD_IMAGES_COUNT, "*"],
    ],
)
def test_filter(driver, browser, count, model):
    driver.get(base_url)

    sign_in(driver, username, password)

    filter_history_model(driver, browser, model, count)


@pytest.mark.rpa
def test_sort(driver, browser):
    driver.get(base_url)

    sign_in(driver, username, password)

    sort_history_date(driver, browser, True)
    sort_history_date(driver, browser, False)


@pytest.mark.rpa
def test_search(driver, browser):
    driver.get(base_url)

    sign_in(driver, username, password)

    for label in list(class_keys.keys()):
        search_history_label(driver, browser, label)


@pytest.mark.rpa
def test_delete_history(driver, browser):
    driver.get(base_url)

    sign_in(driver, username, password)

    for image_id in pytest.rpa_image_ids:
        assert delete_history(driver, browser, image_id)

    filter_history_model(driver, browser, "*", 0)  # check that all deleted


@pytest.mark.rpa
def test_sign_out(driver):
    driver.get(base_url)

    sign_in(driver, username, password)

    assert click_sign_out(driver)
    assert check_sign_in_verification(driver)


def check_sign_in_verification(driver):
    print("Checking unauthorised accesses: ", end="")
    driver.get(base_url + "/upload")
    assert driver.current_url.split(base_url)[1] == "/user/sign_in"
    driver.get(base_url + "/history")
    assert driver.current_url.split(base_url)[1] == "/user/sign_in"
    driver.get(base_url + "/prediction")
    assert driver.current_url.split(base_url)[1] == "/user/sign_in"
    return True


def create_account(driver, username, password):
    print("Creating account: ", end="")

    button_text = "Upload Image"
    xpath = f"//div[text()='{button_text}']/ancestor::a"
    element = driver.find_element(By.XPATH, xpath)
    assert element
    element.click()

    assert driver.current_url.split(base_url)[1] == "/user/sign_in"

    link_text = "Create new account"
    link = driver.find_element(By.LINK_TEXT, link_text)
    assert link
    link.click()

    assert driver.current_url.split(base_url)[1] == "/user/sign_up"

    assert key_in_details(driver, username, password)

    element_exists = driver.find_elements(By.CLASS_NAME, "alert-danger")

    if element_exists:
        print("Account exists.")
        driver.get(base_url + "/user/sign_in")
    else:
        assert driver.current_url.split(base_url)[1] == "/user/sign_in"

    assert key_in_details(driver, username, password)
    assert driver.current_url.split(base_url)[1] == "/upload"


def sign_in(driver, username, password):
    driver.get(base_url + "/user/sign_in")

    assert driver.current_url.split(base_url)[1] == "/user/sign_in"

    assert key_in_details(driver, username, password)

    assert driver.current_url.split(base_url)[1] == "/upload"


# Input the generated username into the field
def key_in_details(driver, username, password):
    input_element = driver.find_element(By.ID, "username")
    assert input_element
    input_element.send_keys(username)

    input_element = driver.find_element(By.ID, "password")
    assert input_element
    input_element.send_keys(password)

    submit = driver.find_element(By.ID, "submit")
    assert submit
    submit.click()

    return True


def upload_image(driver, model):
    print(f"Uploading an image, model size: {model}", end="")
    driver.get(base_url + "/upload")
    file_input = driver.find_element(By.ID, "fileUpload")
    image_file = fake.random_element(pytest.image_files)
    file_path = os.path.join(pytest.image_folder_path, image_file)
    assert file_input
    assert file_path
    file_input.send_keys(file_path)

    driver.implicitly_wait(2)

    model_select = driver.find_element(By.ID, "model")
    assert model_select
    select = Select(model_select)
    assert select
    select.select_by_visible_text(model)
    submit = driver.find_element(By.ID, "submitButton")
    assert submit
    submit.click()

    redirect_substring = "/prediction"
    WebDriverWait(driver, 10).until(EC.url_contains(redirect_substring))

    prediction_url = driver.current_url.split(base_url)[1]
    assert "/prediction" in prediction_url

    image_id = prediction_url.split("image_id=")[1]

    assert str(image_id).isnumeric()

    return image_id


def try_click_next_page(driver, browser, curr_page):
    # Click on the "Next Page" link
    next_page_link = driver.find_elements(By.ID, "next_page")

    if next_page_link:
        if browser != "firefox":
            driver.execute_script("arguments[0].scrollIntoView();", next_page_link[0])

            next_page_link[0].click()
            print("Next Page link found.")
        else:

            actions = ActionChains(driver)
            actions.key_down(Keys.PAGE_DOWN)
            actions.perform()

            next_page_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "next_page"))
            )

            actions.key_up(Keys.PAGE_DOWN)
            actions.perform()

            time.sleep(2)

            driver.execute_script("arguments[0].scrollIntoView();", next_page_link)

            next_page_link.click()

        return True
    print("Next Page link not found. Exiting...")
    return False


def filter_history_model(driver, browser, model, n_entries):
    print(f"Filtering prediction entries by model {model}: ")
    driver.get(base_url + "/history")
    model_select = driver.find_element(By.ID, "model")
    assert model_select
    select = Select(model_select)
    assert select
    select.select_by_visible_text(model)
    submit = driver.find_element(By.ID, "sort")
    assert submit
    submit.click()

    all_rows = []

    while True:
        curr_page = 1

        rows = driver.find_elements(
            By.ID,
            "prediction_id",
        )

        rows = driver.find_elements(
            By.ID,
            "prediction_model",
        )

        all_rows += [row.text for row in rows]

        if not try_click_next_page(driver, browser, curr_page):
            break
        curr_page += 1

    for text in all_rows:
        if model != "*":
            assert text == model

    assert len(all_rows) == n_entries


def sort_history_date(driver, browser, date_oldest_first):
    if date_oldest_first:
        order = "Ascending (Oldest first)"
    else:
        order = "Descending (Latest first)"
    print(f"Sorting prediction entries by date {order}: ")

    driver.get(base_url + "/history")
    date_select = driver.find_element(By.ID, "date_oldest_first")
    assert date_select
    select = Select(date_select)
    assert select
    select.select_by_visible_text(order)
    submit = driver.find_element(By.ID, "sort")
    assert submit
    submit.click()
    all_rows = []

    while True:
        curr_page = 1

        rows = driver.find_elements(
            By.ID,
            "prediction_id",
        )

        all_rows += [row.text for row in rows]

        if not try_click_next_page(driver, browser, curr_page):
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


def search_history_label(driver, browser, label):
    print(f"Filtering prediction entries by label {label}: ")

    driver.get(base_url + "/history")
    input_element = driver.find_element(By.ID, "label")
    assert input_element
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

        if not try_click_next_page(driver, browser, curr_page):
            break
        curr_page += 1

    for text in all_rows:
        assert text == label


def delete_history(driver, browser, image_id):
    while True:
        curr_page = 1
        try:
            driver.get(base_url + "/history")
            delete_button = driver.find_element(
                By.XPATH,
                f'//tr[.//span[text()="{image_id}"]]//button[contains(., "Delete")]',
            )

            assert delete_button

            delete_button.click()
            print(f"Image with ID {image_id} deleted")
            return True
        except NoSuchElementException:
            # Handle the case where the delete button is not found
            print(f"Delete button not found for image ID {image_id}")
            if not try_click_next_page(driver, browser, curr_page):
                return False
            curr_page += 1


def click_sign_out(driver):
    print("Signing out: ", end="")
    sign_out_link = driver.find_element(By.XPATH, '//a[@href="/user/sign_out"]')
    assert sign_out_link
    sign_out_link.click()
    assert sign_out_link
    return True
