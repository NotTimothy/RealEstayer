use log::{info, trace, warn};
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use std::net::SocketAddr;
use axum_server::tls_rustls::RustlsConfig;
use std::sync::Arc;
use axum::{
    routing::{get},
    Router,
};
use tower_http::cors::{Any, CorsLayer};

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

pub fn setup_logging() {
    // Create file appender
    let file_appender = RollingFileAppender::new(
        Rotation::DAILY,
        "logs",
        "dota-trends.log",
    );

    // Create an EnvFilter that enables everything
    let filter = EnvFilter::new("trace,hyper=debug,tower_http=debug")
        .add_directive(LevelFilter::TRACE.into());

    // Create the subscriber
    let subscriber = tracing_subscriber::registry()
        .with(fmt::Layer::new()
            .with_file(true)
            .with_line_number(true)
            .with_thread_ids(true)
            .with_thread_names(true)
            .with_span_events(FmtSpan::FULL)
            .with_writer(file_appender)
            .with_ansi(false)
            .with_target(true)
            .with_level(true)
            .with_filter(filter)
        );

    // Set the subscriber as the default
    if let Err(e) = tracing::subscriber::set_global_default(subscriber) {
        eprintln!("Failed to set up logging: {}", e);
    }

    // Log initial startup
    error!("Logging system initialized with TRACE level enabled");
}

#[tokio::main]
fn main() {

}