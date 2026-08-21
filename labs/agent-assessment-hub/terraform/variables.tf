variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "demo-agent-project"
}

variable "region" {
  description = "GCP Region for Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "container_image" {
  description = "Container image URL"
  type        = string
  default     = "gcr.io/demo-agent-project/agent-assessment-hub:latest"
}

variable "gemini_model" {
  description = "Default Gemini model"
  type        = string
  default     = "gemini-2.5-flash"
}
