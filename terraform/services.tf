resource "kubernetes_service" "app" {
  metadata {
    name = var.app
  }
  spec {
    selector = {
      app = kubernetes_deployment.app.metadata.0.labels.app
    }
    port {
      port        = 80
      target_port = 6566
    }
    type = "LoadBalancer"
  }
} 