variable "gcp_project_name" {
  description = "GCP project name"
}

variable "name_prefix" {
  description = "Prefix to be used when naming the different components of Feast"
}

variable "region" {
  description = "Region for GKE and Dataproc cluster"
}

variable "gke_machine_type" {
  description = "GKE node pool machine type"
  default     = "n1-standard-4"
}

variable "gke_node_count" {
  description = "Number of nodes in the GKE default node pool"
  default     = 1
}

variable "gke_disk_size_gb" {
  description = "Disk size for nodes in the GKE default node pool"
  default     = 100
}

variable "gke_disk_type" {
  description = "Disk type for nodes in the GKE default node pool"
  default     = "pd-standard"
}

variable "network" {
  description = "Network for GKE and Dataproc cluster"
}

variable "subnetwork" {
  description = "Subnetwork for GKE and Dataproc cluster"
}

variable "staging_bucket" {
  description = "GCS bucket for staging temporary files required for jobs"
}

variable "redis_tier" {
  description = "GCP Redis instance tier"
  default     = "BASIC"
}

variable "redis_memory_size_gb" {
  description = "Redis memory size in Gb"
  default     = 2
}

variable "feast_sa_secret_name" {
  description = "Kubernetes secret name for Feast GCP service account"
  default     = "feast-gcp-service-account"
}

variable "docker-image" {
    type = string
    description = "Name of the docker image to deploy"
    default = "gcr.io/jchavezar-demo/feast:v1"
}

variable "app" {
    type = string
    description = "Name of the application"
}