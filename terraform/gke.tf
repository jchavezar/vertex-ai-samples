resource "google_container_cluster" "feast_gke_cluster" {
  name       = "${var.name_prefix}-cluster"
  location   = var.region
  network    = var.network
  subnetwork = var.subnetwork

  initial_node_count = var.gke_node_count
  node_config {
    machine_type = var.gke_machine_type
  }

  ip_allocation_policy {
  }
}

data "google_container_cluster" "feast_gke_cluster" {
  location = var.region
  name     = google_container_cluster.feast_gke_cluster.name
  initial_node_count = 3

  node_config {
    machine_type = var.gke_machine_type
    labels = {
        app = var.app_name
    }

    tags = ["app", var.app_name]
  }
}