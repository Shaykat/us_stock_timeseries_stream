output "cloud_run_url" {
  value       = google_cloud_run_v2_service.default.uri
  description = "The URL of the Cloud Run service."
}

output "name" {
  value = google_cloud_run_v2_service.default.name
}