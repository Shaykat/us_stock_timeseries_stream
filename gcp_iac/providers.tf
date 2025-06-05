terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"  # Use the latest version or a specific version
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.gcp_region
  credentials = file("/home/nawrin995/sh-0001-analytics-460921-65f7785bcfbd.json")
}
