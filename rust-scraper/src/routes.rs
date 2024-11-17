use crate::{database, models::*, scraping::{self, get_place_urls, scrape_place_details, scrape_region}};
use axum::{
    extract::{Path, Query},
    http::StatusCode,
    Json,
    response::IntoResponse,
};
use mongodb::bson::{doc, oid::ObjectId};
use serde_json::json;
use std::collections::HashMap;
use std::process::Command;
use tokio::time::sleep;
use std::time::Duration;
use thirtyfour::{ChromiumLikeCapabilities, DesiredCapabilities, WebDriver};
use anyhow::Result;
use log::info;

// Base URL constant
const BASE_URL: &str = "https://www.airbnb.com/";

// List of Canadian provinces and territories
const CANADIAN_PROVINCES: [&str; 13] = [
    "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
    "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
    "Quebec", "Saskatchewan", "Yukon"
];

// List of US states
const US_STATES: [&str; 50] = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
];

// Helper function to construct full URL
fn construct_url(path: &str) -> String {
    if path.starts_with("http") {
        path.to_string()
    } else {
        info!("{}{}", BASE_URL, path);
        format!("{}{}", BASE_URL, path.trim_start_matches('/'))
    }
}

// Helper function to start ChromeDriver
async fn ensure_chromedriver_running() -> Result<()> {
    // Try to connect to existing ChromeDriver
    if reqwest::get("http://localhost:9515/status").is_ok() {
        return Ok(());
    }

    // Start ChromeDriver
    #[cfg(target_os = "windows")]
    let chromedriver_cmd = "chromedriver.exe";

    Command::new(chromedriver_cmd)
        .arg("--port=9515")
        .spawn()
        .map_err(|e| anyhow::anyhow!("Failed to start ChromeDriver: {}", e))?;

    // Wait for ChromeDriver to start
    for _ in 0..10 {
        if reqwest::get("http://localhost:9515/status").is_ok() {
            return Ok(());
        }
        sleep(Duration::from_secs(1)).await;
    }

    Err(anyhow::anyhow!("ChromeDriver failed to start"))
}

/// Helper function to create WebDriver with proper configuration
async fn create_webdriver() -> Result<WebDriver> {
    ensure_chromedriver_running().await?;

    let mut caps = DesiredCapabilities::chrome();

    // Add Chrome options for better reliability
    caps.add_arg("--no-sandbox")?;
    caps.add_arg("--disable-dev-shm-usage")?;
    caps.add_arg("--disable-gpu")?;
    caps.add_arg("--window-size=1920,1080")?;

    // Optional: run headless
    // caps.add_chrome_arg("--headless")?;

    // Create WebDriver with retry logic
    for attempt in 1..=3 {
        match WebDriver::new("http://localhost:9515", caps.clone()).await {
            Ok(driver) => {
                // Navigate to base URL first
                driver.get(BASE_URL).await?;
                return Ok(driver);
            }
            Err(e) if attempt < 3 => {
                log::warn!("WebDriver creation attempt {} failed: {}", attempt, e);
                sleep(Duration::from_secs(2)).await;
            }
            Err(e) => return Err(anyhow::anyhow!("Failed to create WebDriver: {}", e)),
        }
    }

    Err(anyhow::anyhow!("Failed to create WebDriver after 3 attempts"))
}

pub async fn scrape_north_america() -> impl IntoResponse {
    let result = async {
        let mut total_listings = 0;
        let mut canada_listings = 0;
        let mut us_listings = 0;

        let driver = create_webdriver().await?;

        // Scrape Canadian provinces
        for province in CANADIAN_PROVINCES {
            match scrape_region(&driver, province, "Canada").await {
                Ok(count) => {
                    canada_listings += count;
                    total_listings += count;
                }
                Err(e) => log::error!("Error scraping {}, Canada: {}", province, e),
            }
        }

        // Scrape US states
        for state in US_STATES {
            match scrape_region(&driver, state, "USA").await {
                Ok(count) => {
                    us_listings += count;
                    total_listings += count;
                }
                Err(e) => log::error!("Error scraping {}, USA: {}", state, e),
            }
        }

        // Quit the WebDriver session
        if let Err(e) = driver.quit().await {
            log::error!("Error closing WebDriver session: {}", e);
        }

        Ok::<_, anyhow::Error>(Json(ScrapingResponse {
            message: "Scraping completed".to_string(),
            total_listings,
            canada_listings,
            us_listings,
        }))
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Scraping failed: {}", e),
        )
            .into_response(),
    }
}

pub async fn scrape_city_data(
    Query(params): Query<HashMap<String, String>>,
) -> impl IntoResponse {
    let city = match params.get("city") {
        Some(c) => c,
        None => {
            return (StatusCode::BAD_REQUEST, "City parameter is required").into_response()
        }
    };

    let result = async {
        let driver = create_webdriver().await?;

        let urls = get_place_urls(&driver, city).await?;
        let mut place_details = Vec::new();

        for url in urls {
            let full_url = construct_url(&url);
            match scrape_place_details(&driver, &full_url).await {
                Ok(details) => place_details.push(details),
                Err(e) => log::error!("Error scraping {}: {}", full_url, e),
            }
        }

        // Quit the WebDriver session
        if let Err(e) = driver.quit().await {
            log::error!("Error closing WebDriver session: {}", e);
        }

        let inserted_ids = database::insert_many(place_details.clone()).await?;

        Ok::<_, anyhow::Error>(Json(json!({
            "city": city,
            "places": place_details,
            "inserted_ids": inserted_ids,
        })))
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to scrape city data: {}", e),
        )
            .into_response(),
    }
}

// You might also want a version without limit
pub async fn get_listings_without_limit(
    Path(city): Path<String>,
) -> impl IntoResponse {
    let result = async {
        let query = if !city.is_empty() {
            doc! { "location": { "$regex": city, "$options": "i" } }
        } else {
            doc! {}
        };

        let listings = database::get_listings_by_query(query, 10).await?;
        Ok::<_, anyhow::Error>(Json(listings))
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to get listings: {}", e),
        )
            .into_response(),
    }
}

pub async fn get_listings(
    Path((city, limit)): Path<(String, Option<i64>)>, // Extract path parameters
) -> impl IntoResponse {
    let result = async {
        let limit = limit.unwrap_or(10);

        let query = if !city.is_empty() {
            doc! { "location": { "$regex": city, "$options": "i" } }
        } else {
            doc! {}
        };

        let listings = database::get_listings_by_query(query, limit).await?;
        Ok::<_, anyhow::Error>(Json(listings))
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to get listings: {}", e),
        )
            .into_response(),
    }
}

pub async fn filters(Query(params): Query<HashMap<String, String>>) -> impl IntoResponse {
    let result = async {
        let search = params.get("search");
        let features: Vec<String> = params
            .get("features")
            .map(|f| f.split(',').map(String::from).collect())
            .unwrap_or_default();
        let limit = params
            .get("limit")
            .and_then(|l| l.parse::<i64>().ok())
            .unwrap_or(10);

        let mut query = doc! {};
        if let Some(s) = search {
            query.insert("location", doc! { "$regex": s, "$options": "i" });
        }
        if !features.is_empty() {
            query.insert("features", doc! { "$all": &features });
        }

        let filters_result = database::get_filters(query, limit).await?;
        Ok::<_, anyhow::Error>(Json(filters_result))
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to get filters: {}", e),
        )
            .into_response(),
    }
}

pub async fn get_listing(Path(listing_id): Path<String>) -> impl IntoResponse {
    let result = async {
        let object_id = ObjectId::parse_str(&listing_id)
            .map_err(|_| anyhow::anyhow!("Invalid listing ID"))?;

        match database::get_listing_by_id(object_id).await? {
            Some(listing) => Ok::<_, anyhow::Error>(Json(listing)),
            None => Err(anyhow::anyhow!("Listing not found")),
        }
    }
        .await;

    match result {
        Ok(response) => response.into_response(),
        Err(e) => {
            let (status, message) = match e.to_string().as_str() {
                "Invalid listing ID" => (StatusCode::BAD_REQUEST, "Invalid listing ID"),
                "Listing not found" => (StatusCode::NOT_FOUND, "Listing not found"),
                _ => (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "Failed to get listing",
                ),
            };
            (status, message).into_response()
        }
    }
}

pub async fn info() -> impl IntoResponse {
    Json(json!({
        "environment": std::env::var("ENVIRONMENT").unwrap_or_else(|_| "production".to_string()),
        "status": "running"
    }))
}

pub async fn health() -> impl IntoResponse {
    Json(json!({
        "status": "healthy",
        "environment": std::env::var("ENVIRONMENT").unwrap_or_else(|_| "production".to_string())
    }))
}