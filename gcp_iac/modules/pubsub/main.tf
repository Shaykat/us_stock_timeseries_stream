resource "google_pubsub_schema" "schema" {
  name       = var.schema_name
  type       = "AVRO"
  definition = var.avro_schema_definition
  project    = var.project_id
}

resource "google_pubsub_topic" "topic" {
  name    = var.topic_name
  project = var.project_id
  schema_settings {
    schema   = google_pubsub_schema.schema.id
    encoding = "JSON"
  }
}
