// scraping.rs
use anyhow::{Result, anyhow};
use futures::stream::{FuturesUnordered, StreamExt};
use std::collections::HashSet;
use thirtyfour::{By, WebDriver, WebElement};
use tokio::time::{sleep, Duration};
use tokio::sync::Semaphore;
use std::sync::Arc;
use futures::TryFutureExt;
use crate::models::Listing;
const MAX_CONCURRENT_SCRAPES: usize = 5;
const BASE_URL: &str = "https://www.airbnb.com/";

// Helper function to construct full URLs
fn construct_full_url(path: &str) -> String {
    if path.starts_with("http") {
        path.to_string()
    } else {
        format!("{}{}", BASE_URL, path)//.trim_start_matches('/'))
    }
}

pub async fn get_place_urls(driver: &WebDriver, location: &str) -> Result<Vec<String>> {
    let encoded_location = urlencoding::encode(location);
    let search_url = format!(
        "{}/s/{}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&\
         flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-12-01&monthly_length=12&\
         monthly_end_date=2026-12-01&price_filter_input_type=0&channel=EXPLORE&\
         date_picker_type=flexible_dates&source=structured_search_input_header&adults=3&\
         search_type=autocomplete_click&query={}",
        BASE_URL, encoded_location, encoded_location
    );

    driver.goto(&search_url).await?;
    let mut urls = HashSet::new();
    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENT_SCRAPES));

    loop {
        sleep(Duration::from_secs(8)).await;

        sleep(Duration::from_millis(fastrand::u64(1000..3000))).await;

        let places = driver.find_all(By::ClassName("atm_7l_1j28jx2")).await?;
        let mut tasks: FuturesUnordered<_> = places.into_iter().map(|place| {
            let permit = semaphore.clone().acquire_owned();
            async move {
                let _permit = permit.await?;
                if let Ok(Some(href)) = place.attr("href").await {
                    Ok::<Option<String>, anyhow::Error>(Some(construct_full_url(&href)))
                } else {
                    Ok::<Option<String>, anyhow::Error>(None)
                }
            }
        }).collect();

        while let Some(result) = tasks.next().await {
            if let Ok(Some(url)) = result {
                urls.insert(url);
            }
        }

        log::info!("Found {} unique places so far", urls.len());

        match driver.find(By::XPath("//a[@aria-label='Next']")).await {
            Ok(next_button) => {
                if next_button.is_clickable().await? {
                    next_button.click().await?;
                    // Increase wait time after pagination
                    sleep(Duration::from_secs(10)).await;
                } else {
                    break;
                }
            }
            Err(_) => break,
        }
    }

    Ok(urls.into_iter().collect())
}

// Rest of the helper functions remain unchanged
async fn close_modal(driver: &WebDriver) -> Result<()> {
    if let Ok(close_button) = driver.find(By::XPath("//button[@aria-label='Close']")).await {
        if close_button.is_clickable().await? {
            close_button.click().await?;
            sleep(Duration::from_secs(1)).await;
            log::info!("Successfully closed modal");
        }
    }
    Ok(())
}

async fn click_show_all_amenities(driver: &WebDriver) -> Result<bool> {
    close_modal(driver).await?;

    if let Ok(button) = driver
        .find(By::XPath("//button[contains(., 'Show all') and contains(., 'amenities')]"))
        .await
    {
        driver.execute(
            "arguments[0].scrollIntoView(true);",
            vec![serde_json::json!({"element": button.element_id()})],
        )
            .await?;

        sleep(Duration::from_secs(1)).await;

        driver.execute(
            "arguments[0].click();",
            vec![serde_json::json!({"element": button.element_id()})],
        )
            .await?;

        driver.find(By::ClassName("twad414")).await?;
        log::info!("Successfully clicked 'Show all amenities' button");
        Ok(true)
    } else {
        log::warn!("Failed to find 'Show all amenities' button");
        Ok(false)
    }
}

async fn scrape_features(driver: &WebDriver) -> Result<Vec<String>> {
    if click_show_all_amenities(driver).await? {
        let elements = driver.find_all(By::ClassName("twad414")).await?;
        scrape_elements_parallel(elements).await
    } else {
        let elements = driver
            .find_all(By::XPath("//div[contains(@class, 'amenities')]//div[contains(@class, 'title')]"))
            .await?;
        scrape_elements_parallel(elements).await
    }
}

async fn scrape_elements_parallel(elements: Vec<WebElement>) -> Result<Vec<String>> {
    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENT_SCRAPES));
    let mut tasks: FuturesUnordered<_> = elements
        .into_iter()
        .map(|element| {
            let permit = semaphore.clone().acquire_owned();
            async move {
                let _permit = permit.await?;
                let text = element.text().await?;
                Ok::<String, anyhow::Error>(text)
            }
        })
        .collect();

    let mut results = Vec::new();
    while let Some(result) = tasks.next().await {
        if let Ok(text) = result {
            results.push(text);
        }
    }

    Ok(results)
}

async fn scrape_house_details(driver: &WebDriver) -> Result<Vec<String>> {
    let elements = driver.find_all(By::ClassName("l7n4lsf")).await?;
    let details_futures = elements.into_iter().map(|element| async move {
        element.text().await
    });

    let details = futures::future::join_all(details_futures)
        .await
        .into_iter()
        .filter_map(|r| r.ok())
        .collect();

    log::info!("Scraped the details about the AirBnB");
    Ok(details)
}

async fn get_text_or_empty(driver: &WebDriver, by: By) -> Result<String> {
    match driver.find(by).await {
        Ok(element) => {
            Ok(element.text().await.unwrap_or_else(|_| String::new()))
        }
        Err(_) => Ok(String::new()),
    }
}

async fn get_attribute_or_empty(driver: &WebDriver, by: By, attribute: &str) -> Result<String> {
    match driver.find(by).await {
        Ok(element) => {
            match element.attr(attribute).await {
                Ok(Some(value)) => Ok(value),
                _ => Ok(String::new()),
            }
        }
        Err(_) => Ok(String::new()),
    }
}

async fn get_price(driver: &WebDriver, by: By) -> Result<String> {
    let elements = driver.find_all(by).await?;
    for element in elements {
        if let Ok(text) = element.text().await {
            if text.contains('$') {
                return Ok(text.trim().to_string());
            }
        }
    }
    Ok(String::new())
}

pub async fn scrape_place_details(driver: &WebDriver, url: &str) -> Result<Listing> {
    // Ensure we have a full URL before navigating
    let full_url = construct_full_url(url);
    driver.goto(&full_url).await?;
    // Increase page load wait time
    sleep(Duration::from_secs(8)).await;

    // Add random delay variation to avoid detection
    sleep(Duration::from_millis(fastrand::u64(1000..3000))).await;

    let listing = Listing {
        id: None,
        url: full_url,  // Store the full URL in the listing
        title: get_text_or_empty(driver, By::Tag("h1")).await?,
        picture_url: get_attribute_or_empty(driver, By::ClassName("itu7ddv"), "src").await?,
        description: get_text_or_empty(driver, By::ClassName("l1h825yc")).await?,
        price: get_price(driver, By::ClassName("_j1kt73")).await?,
        rating: get_text_or_empty(driver, By::ClassName("r1dxllyb")).await?,
        location: get_text_or_empty(driver, By::ClassName("_152qbzi")).await?,
        features: scrape_features(driver).await?,
        house_details: scrape_house_details(driver).await?,
        region: None,
        country: None,
    };

    log::info!("Scraped details for: {}", listing.title);
    Ok(listing)
}

pub async fn scrape_region(driver: &WebDriver, region: &str, country: &str) -> Result<i32> {
    log::info!("Scraping listings for {}, {}", region, country);

    let place_urls = get_place_urls(driver, &format!("{}, {}", region, country)).await?;
    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENT_SCRAPES));
    let mut tasks: FuturesUnordered<_> = place_urls
        .into_iter()
        .map(|url| {
            let permit = semaphore.clone().acquire_owned();
            let driver = driver.clone();
            async move {
                let _permit = permit.await?;
                let mut details = scrape_place_details(&driver, &url).await?;
                details.region = Some(region.to_string());
                details.country = Some(country.to_string());
                Ok::<Listing, anyhow::Error>(details)
            }
        })
        .collect();

    let mut region_listings = Vec::new();
    while let Some(result) = tasks.next().await {
        if let Ok(listing) = result {
            region_listings.push(listing);
        }
    }

    let inserted_ids = crate::database::insert_many(region_listings).await?;
    let count = inserted_ids.len() as i32;
    log::info!("Inserted {} listings for {}, {}", count, region, country);

    Ok(count)
}