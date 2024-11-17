mod models;
mod database;
mod routes;
mod scraping;


use log::{error, info, trace, warn};
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::{fmt::{self, format::FmtSpan}, prelude::*, filter::LevelFilter, EnvFilter};
use std::net::SocketAddr;
use axum_server::tls_rustls::RustlsConfig;
use std::sync::Arc;
use axum::{
    routing::{get},
    Router,
};
use tower_http::cors::{Any, CorsLayer};

pub fn setup_logging() {
    // Create file appender
    let file_appender = RollingFileAppender::new(
        Rotation::DAILY,
        "logs",
        "realestayer-scraper.log",
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
async fn main() {
    // Initialize logging first
    setup_logging();

    // Start your application...
    tracing::info!("Starting application...");

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/scrape-north-america", get(routes::scrape_north_america))
        .route("/scrape-city-data", get(routes::scrape_city_data))
        .route("/get-listings", get(routes::get_listings))
        .route("/filters", get(routes::filters))
        .route("/get-listings/{city}/{limit}", get(routes::get_listings))
        .route("/get-listings/{city}", get(routes::get_listings_without_limit))
        .route("/get-listing/{listing_id}", get(routes::get_listing))
        .route("/info", get(routes::info))
        .route("/health", get(routes::health))

        .layer(cors);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8782")
        .await
        .expect("Failed to start server.");
    tracing::debug!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
    
    // Configure the domain and certificate
    // let config = RustlsConfig::from_pem_file(
    //     "./fullchain.pem", // /usr/local/bin
    //     "./privkey.pem", // /usr/local/bin
    // )
    //     .await
    //     .expect("Failed to load certificate and private key");

    // Run the server
    // let addr = SocketAddr::from(([0, 0, 0, 0], 8782));
    // axum_server::bind_rustls(addr, config)
    //     .serve(app.into_make_service())
    //     .await
    //     .expect("Failed to start server");
}