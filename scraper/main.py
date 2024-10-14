import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def initialize_browser():
    browser = webdriver.Chrome()
    url = 'https://www.airbnb.com/s/Lake-Superior--MN--USA/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-08-01&monthly_length=3&monthly_end_date=2024-11-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&query=Lake%20Superior%2C%20MN&place_id=ChIJzV1LHgfwpVIRmrBTDYA1Jio&location_bb=QkDSv8K2Cp5CO4YVwrgYpw%3D%3D&adults=3&source=structured_search_input_header&search_type=autocomplete_click'
    browser.get(url)
    return browser


def wait_for_elements(browser, by, value, timeout=10):
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )


def get_text_or_empty(browser, by, value):
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return element.text
    except (TimeoutException, NoSuchElementException):
        return ""


def get_attribute_or_empty(browser, by, value, attribute):
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return element.get_attribute(attribute)
    except (TimeoutException, NoSuchElementException):
        return ""


def get_place_urls(browser):
    urls = set()
    while True:
        places_to_stay = wait_for_elements(browser, By.CLASS_NAME, "atm_7l_1j28jx2")
        for place in places_to_stay:
            url = place.get_attribute('href')
            if url:
                urls.add(url)

        logging.info(f"Found {len(urls)} unique places so far")

        try:
            next_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next']"))
            )
            next_button.click()
            time.sleep(5)
        except (TimeoutException, NoSuchElementException):
            logging.info("Reached the last page or no more results")
            break

    return list(urls)


def scrape_place_details(browser, url):
    browser.get(url)
    time.sleep(5)

    place = {
        "url": url,
        "title": get_text_or_empty(browser, By.TAG_NAME, "h1"),
        "picture_url": get_attribute_or_empty(browser, By.CLASS_NAME, "itu7ddv", "src"),
        "description": get_text_or_empty(browser, By.CLASS_NAME, "l1h825yc"),
        "price": get_text_or_empty(browser, By.CLASS_NAME, "_tyxjp1"),
        "rating": get_text_or_empty(browser, By.CLASS_NAME, "r1dxllyb"),
        "amenities": [amenity.text for amenity in browser.find_elements(By.CLASS_NAME, "l7n4lsf")]
    }

    logging.info(f"Scraped details for: {place['title']}")
    return place


def main():
    browser = initialize_browser()
    place_urls = get_place_urls(browser)

    place_details = []
    for url in place_urls:
        details = scrape_place_details(browser, url)
        place_details.append(details)

    db.insert_many_into_collection(place_details)

    browser.quit()


if __name__ == "__main__":
    main()