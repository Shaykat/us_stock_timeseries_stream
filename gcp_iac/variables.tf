variable "gcp_region" {
  type        = string
  description = "The GCP region to deploy resources to."
  default     = "us-central1"
}

variable "project_id" {
  type        = string
  description = "The GCP project ID."
  default     = "ssh-0001-analytics"
}

variable "artifact_registry_image" {
  type        = string
  description = "The full path to the container image in Artifact Registry."
}

variable "gcs_bucket" {
  type        = string
  description = "The GCS bucket for storing data of the project"
}

variable "bigquery_dataset_id" {
  type        = string
  description = "The ID of the BigQuery dataset."
  default     = "bus_arrival_data"
}

variable "alpha_vantage_api_key" {
  type        = string
  description = "Alpha Vantage API key."
  sensitive   = true  # Mark as sensitive
}
