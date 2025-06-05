output "topic_name" {
  value       = google_pubsub_topic.topic.name
  description = "The name of the Pub/Sub topic."
}

output "topic_id" {
  value       = google_pubsub_topic.topic.id
  description = "The ID of the Pub/Sub topic."
}

output "schema_name" {
  value       = google_pubsub_schema.schema.name
  description = "The name of the Pub/Sub schema."
}

output "schema_id" {
  value       = google_pubsub_schema.schema.id
  description = "The ID of the Pub/Sub schema."
}

output "topic_schema_settings" {
  value       = google_pubsub_topic.topic.schema_settings
  description = "The schema settings block of the Pub/Sub topic."
}
