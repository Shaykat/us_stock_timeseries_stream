# Secret Manager
resource "google_secret_manager_secret" "api_key" {
  secret_id = "us-time-series-api-key"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.name
  secret_data = var.alpha_vantage_api_key  # Use the variable for the API key
}

# Pub/Sub Topic
# Read yaml as local object
locals {
  pubsub_topics = yamldecode(file("topics.yaml"))
}

# Deploy the topics using the Pub/Sub module and for_each
module "pubsub_topics" {
  for_each = local.pubsub_topics
  source   = "./modules/pubsub"

  topic_name           = each.value.topic_name
  schema_name          = each.value.schema_name
  avro_schema_definition = file(each.value.avro_schema_definition)
  project_id           = var.project_id
}

# Cloud Run Module
module "fetch_stock_time_series_cloud_run" {
  source        = "./modules/cloud-run"
  name          = "fetch-arrivals-tf"
  location      = var.gcp_region
  project       = var.project_id
  image         = var.artifact_registry_image
  api_key       = google_secret_manager_secret_version.api_key.name
  pubsub_topic  = google_pubsub_topic.us_stock_time_series_intraday.name  # Pass pubsub_topic
}

# Cloud Scheduler Job
resource "google_cloud_scheduler_job" "us_stock_time_series_scheduler" {
  name     = "us-stock-time-series-scheduler"
  region   = var.gcp_region
  schedule = "* * * * *"  # Every minute
  time_zone = "Etc/UTC"

  http_target {
    http_method = "POST"
    uri         = module.fetch_arrivals_cloud_run.cloud_run_url  # Cloud Run URL from the module
  }
}

# Required for Streaming Dataflow Job Deployment
resource "google_storage_bucket" "gcs_bucket" {
  name                        = var.gcs_bucket
  location                    = var.gcp_region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "dataflow_template_object" {
  name   = "dataflow/dataflow_template.json"
  bucket = google_storage_bucket.gcs_bucket.name
  source = "./gcp_iac/dataflow_template/dataflow_template.json"  # Local path!
}

# BigQuery Dataset
resource "google_bigquery_dataset" "us_stock_time_series" {
  dataset_id = var.bigquery_dataset_id
  location   = var.gcp_region
}

resource "google_dataflow_job" "us_stock_time_series_streaming" {
  name              = "us-stock-time-series-streaming"
  region            = var.gcp_region
  template_gcs_path = "gs://${google_storage_bucket.gcs_bucket.name}/${google_storage_bucket_object.dataflow_template_object.name}"
  depends_on = [google_storage_bucket_object.dataflow_template_object]  # Ensure upload completes first
  parameters = {
    inputTopic          = google_pubsub_topic.us_stock_time_series_intraday.name
    outputTableIntraDay = "${var.project_id}:${var.bigquery_dataset_id}.time_series_intraday"
  }
}
