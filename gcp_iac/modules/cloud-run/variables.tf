variable "name" {
  type        = string
  description = "The name of the Cloud Run service."
}

variable "location" {
  type        = string
  description = "The GCP region for the Cloud Run service."
}

variable "project" {
  type        = string
  description = "The GCP project ID."
}

variable "image" {
  type        = string
  description = "The container image for the Cloud Run service."
}

variable "container_port" {
  type        = number
  description = "The port the container listens on."
  default     = 8080
}

variable "api_key" {
  type        = string
  description = "The API key for the Cloud Run service."
  sensitive   = true
}

variable "cpu" {
  type        = string
  description = "The CPU limit for the Cloud Run container."
  default     = "1"
}

variable "memory" {
  type        = string
  description = "The memory limit for the Cloud Run container."
  default     = "512Mi"
}

variable "min_instance_count" {
  type        = number
  description = "The minimum number of instances for the Cloud Run service."
  default     = 0
}

variable "max_instance_count" {
  type        = number
  description = "The maximum number of instances for the Cloud Run service."
  default     = 5
}

variable "pubsub_topic" {
  type = string
  description = "The name of the Pub/Sub topic to publish to."
}
