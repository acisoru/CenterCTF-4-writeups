extern crate libloading;

use std::sync::Arc;

use axum::{
    Router,
    routing::get,
};
use axum::routing::{post, put};
use kv::{Bucket, Config, Error as KvError, Store};
use rumqttc::QoS;
use serde::Deserialize;
use tokio::sync::Mutex;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use mqtt::MqttPublisher;

mod mqtt;
mod minijit_interop;

mod flagdb;
mod encryption;
mod secret_storage;
mod http;

#[derive(Deserialize)]
struct KubeletQueryParams {
    kube: String,
}

#[tokio::main]
async fn main() -> Result<(), KvError> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();
    let cfg = Config::new("./flags_db").flush_every_ms(10);

    let store = Store::new(cfg)?;
    let kubelet_info: Arc<Bucket<'static, String, String>> = Arc::new(store.bucket::<String, String>(Some("kubelet_info")).unwrap());
    let secret_bucket: Arc<Bucket<'static, String, String>> = Arc::new(store.bucket::<String, String>(Some("secrets")).unwrap());

    let mqtt_publisher = Arc::new(Mutex::new(MqttPublisher::new(kubelet_info.clone().into()).await.expect("Failed to create MQTT publisher")));

    {
        let publisher = mqtt_publisher.lock().await;
        publisher.subscribe("/kube_comms/#", QoS::ExactlyOnce).await.expect("Failed to subscribe to topic");
    }

    // build our application with a route
    let app = Router::new()
        .route("/", get(http::handler))
        .route("/api/client/info", get(http::kubelet_info_handler))
        .route("/api/client/transmit", post(mqtt::transmit_message_handler))
        .route("/api/client/receive", get(mqtt::receive_message_handler))
        .layer(axum::extract::Extension(mqtt_publisher))
        .route("/api/connect_as_new_kube", get(encryption::connect_as_new_kube_handler))
        .layer(axum::extract::Extension(kubelet_info))
        .route("/api/client/secret", put(secret_storage::store_secret_handler))
        .route("/api/client/secret", get(secret_storage::retrieve_secret_handler))
        .layer(axum::extract::Extension(secret_bucket))
        .fallback(http::handler_404);

    // run it
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();
    tracing::debug!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();

    Ok(())
}
