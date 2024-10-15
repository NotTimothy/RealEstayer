import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import db
import logging
from flask import Flask, request, jsonify
from bson.json_util import dumps
import json
from flask_cors import CORS
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


# Database configuration
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"

def initialize_browser():
    browser = webdriver.Chrome()
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

def get_price(browser, by, value):
    try:
        elements = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((by, value))
        )

        for element in elements:
            if '$' in element.text:
                return element.text.strip()

        return ""  # Return empty string if no element with '$' is found
    except (TimeoutException, NoSuchElementException):
        logging.error(f"Error finding price elements: {by}, {value}")
        return ""

def get_attribute_or_empty(browser, by, value, attribute):
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return element.get_attribute(attribute)
    except (TimeoutException, NoSuchElementException):
        return ""

def get_place_urls(browser, location):
    urls = set()
    base_url = f'https://www.airbnb.com/s/{location}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-11-01&monthly_length=3&monthly_end_date=2025-02-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&source=structured_search_input_header&search_type=autocomplete_click&query={location}'
    browser.get(base_url)

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
        "price": get_price(browser, By.CLASS_NAME, "_j1kt73"),
        "rating": get_text_or_empty(browser, By.CLASS_NAME, "r1dxllyb"),
        "location": get_text_or_empty(browser, By.CLASS_NAME, "_152qbzi"),
        "amenities": [amenity.text for amenity in browser.find_elements(By.CLASS_NAME, "l7n4lsf")]
    }

    logging.info(f"Scraped details for: {place['title']}")
    return place

@app.route('/scrape-city-data', methods=['GET'])
def get_city_data():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    browser = initialize_browser()
    try:
        place_urls = get_place_urls(browser, city)
        place_details = []
        # Change when done making changes
        for url in place_urls: # [:10]:  # Limit to 10 places for demonstration
            details = scrape_place_details(browser, url)
            place_details.append(details)

        inserted_ids = db.insert_many_into_collection(place_details)

        return jsonify({
            "city": city,
            "places": json.loads(dumps(place_details)),
            "inserted_ids": inserted_ids
        })
    finally:
        browser.quit()


@app.route('/get-listings', methods=['GET'])
def get_listings():
    city = request.args.get('city')
    limit = int(request.args.get('limit', 10))

    query = {"city": city} if city else {}

    try:
        listings = db.get_listings(DB_NAME, COLLECTION_NAME, query, limit)
        return jsonify(listings)
    except Exception as e:
        logging.error(f"An error occurred while fetching listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500


@app.route('/get-listing/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    try:
        listing = db.get_listing_by_id(DB_NAME, COLLECTION_NAME, listing_id)
        if listing:
            return jsonify(listing)
        else:
            return jsonify({"error": "Listing not found"}), 404
    except Exception as e:
        logging.error(f"An error occurred while fetching the listing: {e}")
        return jsonify({"error": "Failed to fetch the listing"}), 500


if __name__ == "__main__":
    app.run(debug=True)