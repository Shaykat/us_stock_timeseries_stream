# Enable Required services API 
resource "google_project_service" "cloud_resource_manager" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
  disable_dependent_services = false
  project = var.project_id
}

resource "google_project_service" "pubsub" {
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
  project = var.project_id
}

resource "google_project_service" "cloud_run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
  project = var.project_id
}

# Pub/Sub Topic
# Read yaml as local object
locals {
  pubsub_topics = yamldecode(file("topics.yml"))
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
module "fetch_us_stock_time_series_cloud_run" {
  source        = "./modules/cloud-run"
  name          = "us-stock-time-series-producer"
  location      = var.gcp_region
  project       = var.project_id
  image         = var.artifact_registry_image
  api_key       = var.alpha_vantage_api_key
  pubsub_topic  = "time-series-intraday"
}

# Cloud Scheduler Job
resource "google_cloud_scheduler_job" "us_stock_time_series_scheduler" {
  name     = "us-stock-time-series-scheduler"
  region   = var.gcp_region
  schedule = "*/5 * * * *"  # Every minute
  time_zone = "Etc/UTC"

  http_target {
    http_method = "POST"
    uri         = module.fetch_us_stock_time_series_cloud_run.cloud_run_url  # Cloud Run URL from the module
  }
}
