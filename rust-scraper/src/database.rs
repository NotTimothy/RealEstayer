// database.rs
use crate::models::*;
use anyhow::Result;
use futures::TryStreamExt;
use mongodb::{
    bson::{doc, Document},
    options::{ClientOptions, FindOptions},
    Client, Collection, Database
};
use mongodb::bson::oid::ObjectId;
use tokio::sync::OnceCell;


static DB: OnceCell<Database> = OnceCell::const_new();

pub async fn get_collection() -> Collection<Listing> {
    let client_options = ClientOptions::parse("mongodb://192.168.1.71:27017/?retryWrites=true&loadBalanced=false&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000").await.unwrap();
    let client = Client::with_options(client_options).unwrap();
    client.database("airbnb").collection("listings")
}

pub async fn insert_many(listings: Vec<Listing>) -> Result<Vec<String>> {
    let collection = get_collection().await;
    let result = collection.insert_many(listings).await?;
    Ok(result
        .inserted_ids
        .values()
        .map(|id| id.to_string())
        .collect())
}

pub async fn get_listings_by_query(query: Document, limit: i64) -> Result<Vec<Listing>> {
    let collection = get_collection().await;
    // let options = FindOptions::builder().limit(limit).build();
    let mut cursor = collection.find(query).await?;

    let mut listings = Vec::new();
    while let Some(listing) = cursor.try_next().await? {
        listings.push(listing);
    }

    Ok(listings)
}

pub async fn get_listing_by_id(id: ObjectId) -> Result<Option<Listing>> {
    let collection = get_collection().await;
    Ok(collection.find_one(doc! { "_id": id }).await?)
}

pub async fn get_filters(query: Document, limit: i64) -> Result<FiltersResponse> {
    let collection = get_collection().await;

    let pipeline = vec![
        doc! { "$unwind": "$features" },
        doc! { "$group": { "_id": "$features" } },
        doc! { "$sort": { "_id": 1 } },
    ];

    let mut cursor = collection.aggregate(pipeline).await?;
    let mut features = Vec::new();

    while let Some(doc) = cursor.try_next().await? {
        if let Ok(feature) = doc.get_str("_id") {
            features.push(feature.to_string());
        }
    }

    let listings = get_listings_by_query(query, limit).await?;

    Ok(FiltersResponse {
        features,
        listings,
    })
}