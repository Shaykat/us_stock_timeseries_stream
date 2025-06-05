resource "google_cloud_run_v2_service" "default" {
  name     = var.name
  location = var.location
  project  = var.project

  template {
    containers {
      image = var.image
      ports {
        container_port = var.container_port
      }
      env {
        name  = "API_KEY"
        value = var.api_key
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }
    }

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM binding to allow the Cloud Run service to publish to the Pub/Sub topic
resource "google_pubsub_topic_iam_binding" "cloud_run_pubsub" {
  topic   = var.pubsub_topic #reference the pubsub_topic variable
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${google_cloud_run_v2_service.default.service_account}"]
}
