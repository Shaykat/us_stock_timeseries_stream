variable "topic_name" {
  type        = string
  description = "The name of the Pub/Sub topic."
}

variable "schema_name" {
  type        = string
  description = "The name of the Pub/Sub schema."
}

variable "avro_schema_definition" {
  type        = string
  description = "The Avro schema definition (as a JSON string)."
}

variable "project_id" {
  type        = string
  description = "The GCP project ID."
}
