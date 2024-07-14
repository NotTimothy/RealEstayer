mod database;
mod model;
mod routes;

use axum::{routing::{get, post}, Router};
use tower_http::cors::{Any, CorsLayer};
use std::net::SocketAddr;
use std::sync::Arc;
use axum_server::tls_rustls::RustlsConfig;

#[tokio::main]
async fn main() {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()g
        .route("/fetch-approved-events/", get(routes::fetch_approved_events))
        .route("/approve-event/", post(routes::write_approved_event))
        .route("/send-email/", post(routes::send_email_to_approver))
        .route("/fetch-event/:event_id", get(routes::fetch_event))
        .route("/fetch-pending-event/:event_id", get(routes::fetch_pending_event))
        .route("/fetch-pending-events/", get(routes::fetch_pending_events))
        .route("/send-pending-event/", post(routes::write_pending_events))
        .route("/pending-event-count", get(routes::get_pending_event_count))
        .layer(cors);

    // Configure the domain and certificate
    let config = RustlsConfig::from_pem_file(
        "/usr/local/bin/fullchain.pem",
        "/usr/local/bin/privkey.pem",
    )
        .await
        .expect("Failed to load certificate and private key");

    // Run the server
    let addr = SocketAddr::from(([0, 0, 0, 0], 8787));
    axum_server::bind_rustls(addr, config)
        .serve(app.into_make_service())
        .await
        .expect("Failed to start server");
}