output "cloud_run_url" {
  value       = module.fetch_arrivals_cloud_run.cloud_run_url
  description = "The URL of the Cloud Run service."
}

output "pubsub_topic_name" {
  value       = google_pubsub_topic.us_stock_time_series.name
  description = "The name of the Pub/Sub topic."
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.bus_arrival_data.dataset_id
  description = "The ID of the BigQuery dataset."
}
