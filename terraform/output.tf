  output "gke_cluster" {
    value = var.cluster
  }

  output "endpoint" {
    value = kubernetes_service.app.load_balancer_ingress.0.ip
  }