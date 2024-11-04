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
    "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
    "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
    "Quebec", "Saskatchewan", "Yukon"
]

# List of US states
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    # ... (rest of the states)
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


# ... (rest of your helper functions)

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


# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))

    logger.info(f"Starting server on port {port}")
    serve(app, host='127.0.0.1', port=port, threads=6)