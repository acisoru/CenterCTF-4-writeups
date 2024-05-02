use std::convert::Infallible;
use std::ffi::CString;
use std::os::raw::c_char;
use std::sync::Arc;
use std::time::Duration;

use axum::{
    extract::Query,
    response::IntoResponse,
};
use axum::body::Bytes;
use axum::http::StatusCode;
use axum::response::Sse;
use axum::response::sse::Event;
use fnmatch_sys::fnmatch;
use futures_util::Stream;
use kv::Bucket;
use rumqttc::{AsyncClient, ClientError, MqttOptions, Publish, QoS};
use tokio::sync::{broadcast, Mutex};
use tokio::task;
use tokio_stream::StreamExt;

use crate::{flagdb, KubeletQueryParams};
use crate::flagdb::process_mqtt_message;

pub struct MqttPublisher {
    client: Arc<Mutex<AsyncClient>>,
    pub(crate) tx: broadcast::Sender<Publish>,
}

impl MqttPublisher {
    pub async fn new(kubelet_info: Arc<Bucket<'static, String, String>>) -> Result<Self, ClientError> {
        // Options setup (same as before)
        let mut mqttoptions = MqttOptions::new("admin", "mqtt", 18837);
	mqttoptions.set_credentials("admin", "admin");

        let (client, mut eventloop) = AsyncClient::new(mqttoptions, 10);
        let client = Arc::new(Mutex::new(client));

        // Set up a broadcast channel for distributing messages to subscribers
        let (tx, _) = broadcast::channel(100);

        // Run the MQTT event loop
        let tx_clone = tx.clone();
        let client_clone = Arc::clone(&client);

        task::spawn(async move {
            loop {
                match eventloop.poll().await {
                    Ok(notification) => match notification {
                        // On incoming publish on subscribed topics
                        rumqttc::Event::Incoming(rumqttc::Packet::Publish(publish)) => {
                            tracing::info!("Received message on topic {}, msg: {:?}", publish.topic, publish.payload);
                            let _ = tx_clone.send(publish.clone());
                            process_mqtt_message(publish, Arc::clone(&kubelet_info), &client_clone).await;
                        }
                        // Handle other notifications, such as connections and disconnections
                        _ => (),
                    },
                    Err(err) => {
                        // Log the error and potentially handle connection loss or other errors.
                        tracing::error!("Error in MQTT event loop: {:?}", err);
                    }
                }
            }
        });

        Ok(MqttPublisher { client, tx })
    }

    pub async fn subscribe(&self, topic: &str, qos: QoS) -> Result<(), ClientError> {
        let client = self.client.lock().await;
        client.subscribe(topic, qos).await
    }

    pub async fn publish(&self, topic: &str, message: Vec<u8>) -> Result<(), rumqttc::ClientError> {
        let client = self.client.lock().await;
        client.publish(topic, rumqttc::QoS::ExactlyOnce, false, message).await
    }
}


pub(crate) async fn transmit_message_handler(
    Query(kube_params): Query<KubeletQueryParams>,
    axum::extract::Extension(mqtt_publisher): axum::extract::Extension<Arc<Mutex<MqttPublisher>>>,
    body: Bytes,
) -> impl IntoResponse {
    let topic = format!("/kube_comms/{}", kube_params.kube);
    tracing::info!("Transmitting msg on topic {}, msg: {:?}", topic, body);
    let client = mqtt_publisher.lock().await;

    match client.publish(&topic, Vec::from(body)).await {
        Ok(_) => {
            tracing::info!("Message sent to MQTT topic: {}", topic);
            StatusCode::OK
        }
        Err(e) => {
            tracing::error!("Error sending MQTT message: {:?}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        }
    }
}

pub(crate) async fn receive_message_handler(
    Query(kube_params): Query<KubeletQueryParams>,
    axum::extract::Extension(mqtt_publisher): axum::extract::Extension<Arc<Mutex<MqttPublisher>>>,
) -> Sse<impl Stream<Item=Result<Event, Infallible>>> {
    let kube_id = kube_params.kube;
    let mqtt_publisher = mqtt_publisher.lock().await;
    let rx = mqtt_publisher.tx.subscribe();

    // let kubelet_info = store.bucket::<String, String>(Some("kubelet_info")).unwrap();

    let stream = tokio_stream::wrappers::BroadcastStream::new(rx)
        .filter_map(move |msg| {
            let kube_filter = kube_id.clone(); // Clone kube_id for each message
            match msg {
                Ok(publish) => {
                    // Convert Rust string to C-style string
                    let topic_cstr = CString::new(publish.topic).unwrap();
                    let pattern_cstr = CString::new(format!("/kube_comms/{}", kube_filter)).unwrap();

                    // Use fnmatch to compare the topic and pattern
                    let match_result = unsafe { fnmatch(pattern_cstr.as_ptr() as *const c_char, topic_cstr.as_ptr() as *const c_char, 0) };

                    if match_result == 0 {
                        let temp = String::from_utf8_lossy(&publish.payload);
                        let event_data = temp.as_ref();
                        let san_evdata = flagdb::sanitize_flag(event_data);
                        if flagdb::is_valid_flag(&san_evdata, 4096) {
                            Some(Ok(Event::default().data(san_evdata)))
                        } else { None }
                    } else {
                        // If not, skip the message
                        None
                    }
                }
                Err(_) => Some(Ok(Event::default().data("Error receiving message"))),
            }
        });
    Sse::new(stream).keep_alive(
        axum::response::sse::KeepAlive::new()
            // The interval at which a keep-alive message will be sent
            .interval(Duration::from_secs(1))
            // The content of the keep-alive message
            .text("keep-alive-text"),
    )
}


