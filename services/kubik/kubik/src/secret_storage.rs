use std::sync::Arc;

use axum::body::Bytes;
use axum::extract::Query;
use axum::response::IntoResponse;
use http::StatusCode;
use kv::Bucket;

use crate::{flagdb, KubeletQueryParams};

pub(crate) async fn store_secret_handler(
    Query(kube_params): Query<KubeletQueryParams>,
    axum::extract::Extension(secret_bucket): axum::extract::Extension<Arc<Bucket<'_, String, String>>>,
    body: Bytes,
) -> impl IntoResponse {
    let temp = String::from_utf8_lossy(&body);
    let secret = temp.as_ref();
    let san_secret = flagdb::sanitize_flag(secret);
    if flagdb::is_valid_flag(&san_secret, 64) {
        secret_bucket.set(&kube_params.kube, &secret.to_string()).unwrap();
        StatusCode::OK
    } else { StatusCode::FORBIDDEN }
}

pub(crate) async fn retrieve_secret_handler(
    Query(kube_params): Query<KubeletQueryParams>,
    axum::extract::Extension(secret_bucket): axum::extract::Extension<Arc<Bucket<'_, String, String>>>,
) -> impl IntoResponse {
    match secret_bucket.get(&kube_params.kube) {
        Ok(Some(secret)) => {
            (StatusCode::OK, secret)
        }
        Ok(None) => {
            (StatusCode::NOT_FOUND, "No secret found for the given kube".to_string())
        }
        Err(err) => {
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Error retrieving secret: {}", err))
        }
    }
}