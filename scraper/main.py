# app.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import db
import logging
from flask import Flask, request, jsonify
from bson.json_util import dumps
import json
from flask_cors import CORS
import re
import os
from waitress import serve
from config import config

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# List of Canadian provinces and territories
CANADIAN_PROVINCES = [
    # "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
    # "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
    # "Quebec", "Saskatchewan",
    "Yukon"
]

# List of US states
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

# Initialize Flask app
app = Flask(__name__)
allowed_origin = os.getenv('CORS_ORIGIN', 'http://localhost:6969')
CORS(app, resources={r"/*": {"origins": allowed_origin}})

# Database configuration
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"


# Your existing helper functions
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
    base_url = f'https://www.airbnb.com/s/{location}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-12-01&monthly_length=12&monthly_end_date=2026-12-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&source=structured_search_input_header&adults=3&search_type=autocomplete_click&query={location}'
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

def close_modal(browser):
    try:
        close_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']"))
        )
        close_button.click()
        time.sleep(1)
        logging.info("Successfully closed modal")
    except (TimeoutException, NoSuchElementException):
        logging.info("No modal found to close")

def click_show_all_amenities(browser):
    try:
        # Close any open modals first
        close_modal(browser)

        # Wait for the button to be clickable
        button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Show all') and contains(., 'amenities')]"))
        )
        # Scroll the button into view
        browser.execute_script("arguments[0].scrollIntoView(true);", button)
        # Wait a bit for any animations to finish
        time.sleep(1)
        # Try to click the button using JavaScript
        browser.execute_script("arguments[0].click();", button)
        # Wait for the modal to appear
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "twad414"))
        )
        logging.info("Successfully clicked 'Show all amenities' button")
        return True
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        logging.warning(f"Failed to click 'Show all amenities' button: {e}")
        return False

def scrape_features(browser):
    # Try to click the "Show all amenities" button
    if click_show_all_amenities(browser):
        # If successful, scrape features from the modal
        return [feature.text for feature in browser.find_elements(By.CLASS_NAME, "twad414")]
    else:
        # If unsuccessful, try to scrape features from the main page
        return [feature.text for feature in browser.find_elements(By.XPATH, "//div[contains(@class, 'amenities')]//div[contains(@class, 'title')]")]

def scrape_house_details(browser):
    logging.info(f"Scraped the details about the AirBnB.")
    return [details.text for details in browser.find_elements(By.CLASS_NAME, "l7n4lsf")]

def scrape_place_details(browser, url):
    browser.get(url)
    time.sleep(5)  # Wait for page to load

    place = {"url": url, "title": get_text_or_empty(browser, By.TAG_NAME, "h1"),
             "picture_url": get_attribute_or_empty(browser, By.CLASS_NAME, "itu7ddv", "src"),
             "description": get_text_or_empty(browser, By.CLASS_NAME, "l1h825yc"),
             "price": get_price(browser, By.CLASS_NAME, "_j1kt73"),
             "rating": get_text_or_empty(browser, By.CLASS_NAME, "r1dxllyb"),
             "location": get_text_or_empty(browser, By.CLASS_NAME, "_152qbzi"),
             "features": scrape_features(browser),
             "house_details": scrape_house_details(browser)}

    # Scrape the features

    logging.info(f"Scraped details for: {place['title']}")
    return place

def scrape_region(browser, region, country):
    logging.info(f"Scraping listings for {region}, {country}")
    place_urls = get_place_urls(browser, f"{region}, {country}")
    region_listings = []
    for url in place_urls:
        details = scrape_place_details(browser, url)
        details['region'] = region
        details['country'] = country
        region_listings.append(details)

    # Write the listings for this region to the database
    inserted_ids = db.insert_many_into_collection(DB_NAME, COLLECTION_NAME, region_listings)
    logging.info(f"Inserted {len(inserted_ids)} listings for {region}, {country}")

    return len(inserted_ids)

# Route handlers
@app.route('/scrape-north-america', methods=['GET'])
def scrape_north_america():
    browser = initialize_browser()
    try:
        total_listings = 0
        canada_listings = 0
        us_listings = 0

        # Scrape Canadian provinces
        for province in CANADIAN_PROVINCES:
            canada_listings += scrape_region(browser, province, "Canada")
            total_listings += canada_listings

        # Scrape US states
        for state in US_STATES:
            us_listings += scrape_region(browser, state, "USA")
            total_listings += us_listings

        return jsonify({
            "message": "Scraping completed",
            "total_listings": total_listings,
            "canada_listings": canada_listings,
            "us_listings": us_listings,
        })
    except Exception as e:
        logger.error(f"An error occurred while scraping: {e}")
        return jsonify({"error": "Failed to scrape listings"}), 500
    finally:
        browser.quit()


@app.route('/scrape-city-data', methods=['GET'])
def get_city_data():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    browser = initialize_browser()
    try:
        place_urls = get_place_urls(browser, city)
        place_details = []
        for url in place_urls:
            details = scrape_place_details(browser, url)
            place_details.append(details)

        inserted_ids = db.insert_many_into_collection(DB_NAME, COLLECTION_NAME, place_details)

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
    limit = int(request.args.get('limit', 0))

    query = {}
    if city:
        query["location"] = {"$regex": city, "$options": "i"}

    try:
        listings = db.get_listings(DB_NAME, COLLECTION_NAME, query, limit)
        return jsonify(listings)
    except Exception as e:
        logger.error(f"An error occurred while fetching listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500


@app.route('/filters', methods=['GET'])
def get_filters():
    search_term = request.args.get('search', '')
    features = request.args.get('features', '').split(',') if request.args.get('features') else []
    limit = int(request.args.get('limit', 10))

    query = {}
    if search_term:
        query["location"] = {"$regex": search_term, "$options": "i"}
    if features:
        query["features"] = {"$all": features}

    try:
        filters_result = db.get_filters(DB_NAME, COLLECTION_NAME, query, limit)
        return jsonify(filters_result)
    except Exception as e:
        logger.error(f"An error occurred while fetching filters: {e}")
        return jsonify({"error": "Failed to fetch filters"}), 500


@app.route('/get-listing/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    try:
        listing = db.get_listing_by_id(DB_NAME, COLLECTION_NAME, listing_id)
        if listing:
            return jsonify(listing)
        else:
            return jsonify({"error": "Listing not found"}), 404
    except Exception as e:
        logger.error(f"An error occurred while fetching the listing: {e}")
        return jsonify({"error": "Failed to fetch the listing"}), 500

# Add an info endpoint to check configuration
@app.route('/info', methods=['GET'])
def get_info():
    if config.ENV == 'development':
        return jsonify({
            "environment": config.ENV,
            "host": config.HOST,
            "port": config.PORT,
            "cors_origins": config.CORS_ORIGINS
        })
    return jsonify({
        "environment": config.ENV,
        "status": "running"
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "environment": config.ENV
    }), 200


if __name__ == "__main__":
    logger.info(f"Starting {config.ENV} server on {config.HOST}:{config.PORT}")
    logger.info(f"CORS origins: {config.CORS_ORIGINS}")

    if config.ENV == 'development':
        # Use Flask's development server
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    else:
        # Use waitress for production
        serve(app, host=config.HOST, port=config.PORT, threads=6)
