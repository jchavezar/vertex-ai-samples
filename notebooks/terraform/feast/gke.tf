resource "google_container_cluster" "feast_gke_cluster" {
  name       = "${var.name_prefix}-cluster"
  location   = var.region
  network    = var.network
  subnetwork = var.subnetwork
  remove_default_node_pool = true
  initial_node_count = var.gke_node_count
}
resource "google_container_node_pool" "primary_preemptible_nodes" {
  name = "{var.name_prefix}-node-pool"
  location = var.region
  cluster = google_container_cluster.feast_gke_cluster.name
  node_count = 1
  node_config {
    preemptible =  true
    machine_type = var.gke_machine_type
    labels = {
      app = var.app
    }

    tags = ["app", var.app]
  }
}