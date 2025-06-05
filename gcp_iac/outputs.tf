output "cloud_run_url" {
  value       = module.fetch_us_stock_time_series_cloud_run.cloud_run_url
  description = "The URL of the Cloud Run service."
}

output "pubsub_topic_name" {
  value       = "time-series-intraday"
  description = "The name of the Pub/Sub topic."
}

# output "bigquery_dataset_id" {
#   value       = google_bigquery_dataset.bus_arrival_data.dataset_id
#   description = "The ID of the BigQuery dataset."
# }
