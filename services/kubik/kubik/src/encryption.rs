use axum::Json;
use axum::response::IntoResponse;
use http::StatusCode;
use rand::distributions::Alphanumeric;
use rand::Rng;
use serde_json::json;

pub(crate) async fn connect_as_new_kube_handler() -> impl IntoResponse {
    let kube_id: String = rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(32)
        .map(char::from)
        .collect();

    let response = json!({
        "kube_id": kube_id,
    });

    (StatusCode::OK, Json(response))
}
