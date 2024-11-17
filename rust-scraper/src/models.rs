// models.rs
use serde::{Deserialize, Serialize};
use mongodb::bson::oid::ObjectId;

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub environment: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InfoResponse {
    pub environment: String,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Listing {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub url: String,
    pub title: String,
    pub picture_url: String,
    pub description: String,
    pub price: String,
    pub rating: String,
    pub location: String,
    pub features: Vec<String>,
    pub house_details: Vec<String>,
    pub region: Option<String>,
    pub country: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FiltersResponse {
    pub features: Vec<String>,
    pub listings: Vec<Listing>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ScrapingResponse {
    pub message: String,
    pub total_listings: i32,
    pub canada_listings: i32,
    pub us_listings: i32,
}