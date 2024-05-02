use std::collections::HashSet;
use std::sync::Arc;

use kv::Bucket;
use rumqttc::{AsyncClient, Publish};
use serde_json::json;
use serde_json::Value;
use tokio::sync::Mutex;

async fn execute_code(code: &str) -> String {
    crate::minijit_interop::execute_program(code).to_string()
}

pub(crate) async fn process_mqtt_message(publish: Publish, kubelet_info: Arc<Bucket<'_, String, String>>, client: &Arc<Mutex<AsyncClient>>) {
    let topic_parts: Vec<&str> = publish.topic.split('/').collect();
    if topic_parts.len() == 3 && topic_parts[1] == "kube_comms" {
        let kube_id = topic_parts[2];
        let event_data = String::from_utf8_lossy(&publish.payload).to_string();

        if let Ok(json) = serde_json::from_str::<Value>(&event_data) {
            match json.get("e").and_then(Value::as_str) {
                Some("add_flag") => {
                    if let Some(flag) = json.get("flag").and_then(Value::as_str) {
                        // Validate and sanitize the flag value
                        let sanitized_flag = sanitize_flag(flag);
                        if is_valid_flag(&sanitized_flag, 64) {
                            kubelet_info.set(&kube_id.to_string(), &sanitized_flag).unwrap();
                        } else {
                            // Handle invalid flag value
                            tracing::warn!("Invalid flag value received: {}", flag);
                        }
                    }
                }
                Some("execute_on_cloud_accelerator") => {
                    if let Some(code) = json.get("code").and_then(Value::as_str) {
                        // Execute some code and return the result
                        let result = execute_code(code).await;
                        let response = json!({
                            "cloud_accel_result": result
                        });
                        // Publish the result to the same topic
                        let client = client.lock().await;
                        let _ = client.publish(&format!("/kube_comms/{}", kube_id), rumqttc::QoS::ExactlyOnce, false, response.to_string().into_bytes()).await;
                    }
                }
                _ => {}
            }
        }
    }
}


pub(crate) fn sanitize_flag(flag: &str) -> String {
    let allowed_chars = "\\_{}:,=\" ".chars().collect::<HashSet<char>>();
    flag.chars().filter(|c| c.is_alphanumeric() || allowed_chars.contains(c)).collect()
}

pub(crate) fn is_valid_flag(flag: &str, upper_bound: usize) -> bool {
    flag.len() >= 4 && flag.len() <= upper_bound
}