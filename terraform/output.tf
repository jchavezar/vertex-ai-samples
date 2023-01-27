  output "gke_cluster" {
    value = google_container_cluster.feast_gke_cluster.name
  }

  output "endpoint" {
    value = kubernetes_service.app.load_balancer_ingress.0.ip
  }