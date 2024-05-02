use std::sync::Arc;

use axum::extract::Query;
use axum::Json;
use axum::response::{Html, IntoResponse};
use http::StatusCode;
use kv::Bucket;

use crate::KubeletQueryParams;

pub(crate) async fn handler() -> Html<&'static str> {
    Html("<h1>i found 2 vulnerabilities in this service, and how much can you find?</h1>")
}

pub(crate) async fn kubelet_info_handler(
    Query(params): Query<KubeletQueryParams>,
    axum::extract::Extension(kubelet_info): axum::extract::Extension<Arc<Bucket<'_, String, String>>>,
) -> impl IntoResponse {
    // Get the kubelet id from the query parameters
    let kube_id = params.kube;

    // Check if the kubelet info exists in the bucket
    match kubelet_info.get(&kube_id) {
        Ok(Some(flag)) => {
            // Respond with the actual info in JSON format
            (StatusCode::OK, Json(flag))
        }
        Ok(None) => {
            // If the kubelet does not exist in the bucket, respond with an error
            (
                StatusCode::NOT_FOUND,
                Json(format!("No info found for kubelet {}", kube_id)),
            )
        }
        Err(err) => {
            // Handle the error case and return an appropriate response
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(format!("Error retrieving kubelet info: {}", err)),
            )
        }
    }
}


pub(crate) async fn handler_404() -> impl IntoResponse {
    (StatusCode::NOT_FOUND, "nothing to see here")
}