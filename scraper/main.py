import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import db


def initialize_browser():
    browser = webdriver.Chrome()
    url = 'https://www.airbnb.com/s/Lake-Superior--MN--USA/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-08-01&monthly_length=3&monthly_end_date=2024-11-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&query=Lake%20Superior%2C%20MN&place_id=ChIJzV1LHgfwpVIRmrBTDYA1Jio&location_bb=QkDSv8K2Cp5CO4YVwrgYpw%3D%3D&adults=3&source=structured_search_input_header&search_type=autocomplete_click'
    browser.get(url)
    return browser


def wait_for_element(browser, by, value, timeout=10):
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )


def get_place_urls(browser):
    places = set()
    page_numbers = wait_for_element(browser, By.CLASS_NAME, "atm_70_1agwrbf_pfnrn2_1oszvuo")

    for page in range(len(page_numbers)):
        if page > 0:
            page_numbers[page].click()
            time.sleep(5)

        places_to_stay = wait_for_element(browser, By.CLASS_NAME, "atm_7l_1j28jx2")

        for place in places_to_stay:
            url = place.get_attribute('href')
            if url:
                places.add(url)

        print(f"Page {page + 1}: Found {len(places)} unique places so far")

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)

    return list(places)


def scrape_place_details(browser, url):
    browser.get(url)
    time.sleep(5)

    # Here you can add more scraping logic to get details about the place
    # For now, we'll just return the URL as a placeholder
    return {"url": url}


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