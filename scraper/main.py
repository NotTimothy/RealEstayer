import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import db

count = 0
flag = True
places = []
urls = []

browser = webdriver.Chrome()
browser.get('https://www.airbnb.com/s/Lake-Superior--MN--USA/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-08-01&monthly_length=3&monthly_end_date=2024-11-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&query=Lake%20Superior%2C%20MN&place_id=ChIJzV1LHgfwpVIRmrBTDYA1Jio&location_bb=QkDSv8K2Cp5CO4YVwrgYpw%3D%3D&adults=3&source=structured_search_input_header&search_type=autocomplete_click')

time.sleep(10)

page_numbers = browser.find_elements(By.CLASS_NAME, "atm_70_1agwrbf_pfnrn2_1oszvuo")

time.sleep(10)

print(page_numbers)

while flag:
    if count == 0:
        print("If loop.")

        time.sleep(10)

        places_to_stay = browser.find_elements(By.CLASS_NAME, "atm_7l_1j28jx2")

        time.sleep(10)

        print(f"Len: {len(places_to_stay)}")
        print(f"Count: {count}")

        for place in places_to_stay:
            print(place.get_attribute('href'))
            if place.get_attribute('href') not in places:
                places.append(place.get_attribute('href'))

        time.sleep(10)

        count += 1
    elif count > 0 and not count >= len(page_numbers):
        print("Elif loop.")

        time.sleep(10)

        page_numbers[count].click()

        time.sleep(10)

        places_to_stay = browser.find_elements(By.CLASS_NAME, "atm_7l_1j28jx2")

        time.sleep(10)

        print(f"Values: {len(places_to_stay)}")

        time.sleep(10)

        for place in places_to_stay:
            print(place.get_attribute('href'))
            if place.get_attribute('href') not in places:
                places.append(place.get_attribute('href'))

        time.sleep(10)

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        time.sleep(10)

        # if count == 2:
        #     print("Break.")
        #     flag = False

        print(f"Len: {len(places_to_stay)}")
        print(f"Count: {count}")

        count += 1

    else:
        break


for place in places:
    time.sleep(10)

    browser.get(place)

    time.sleep(10)

    info_about_airbnb = browser.find_elements(By.CLASS_NAME, "l7n4lsf")
    is_a_favorite = browser.find_element(By.CLASS_NAME, "lbjrbi0")
    show_more = browser.find_elements(By.CLASS_NAME, "atm_7l_dezgoh_1w3cfyq")

    urls.append(browser.current_url)

db.insert_many_into_collection(places)



