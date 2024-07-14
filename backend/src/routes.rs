
use std::time::Duration;
use axum::{
    extract::Path,
    http::StatusCode,
    Json,
};
use axum::extract::Query;
use axum::response::{IntoResponse, Response};
use mail_send::mail_builder::MessageBuilder;
use mail_send::SmtpClientBuilder;
use serde_json::{json, Value};
use titlecase::titlecase;
use crate::model::*;
use crate::database::*;
use crate::model::model::Event;
use lettre::{Message, SmtpTransport, Transport};
use lettre::message::header::{ContentType, HeaderName};
use lettre::transport::smtp::authentication::Credentials;
use lettre::transport::smtp::client::{Tls, TlsParameters};
use rand::Rng;
use lettre::message::header::MessageId;
use mongodb::bson::doc;
use futures::TryStreamExt;
use mongodb::Database;

pub async fn fetch_airbnb_beach_houses() -> impl IntoResponse {
    let db = database::connect_to_db().await;
    let events: Vec<model::BeachHouse> = database::get_pending_events_from_db(db).await;
    Json(events)
}

pub async fn write_airbnb_beach_houses(Json(payload): Json<model::Event>) -> impl IntoResponse {
    let db = database::connect_to_db().await;

    println!("{:?}", payload);

    database::write_approved_event_to_db(db, payload).await;
    // Return an appropriate response (e.g., success message)
    StatusCode::OK
}
