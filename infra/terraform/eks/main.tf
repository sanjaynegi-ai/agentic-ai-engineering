resource "kubernetes_deployment_v1" "app" {
  metadata {
    name      = var.project_name
    namespace = var.kubernetes_namespace
    labels    = { app = var.project_name }
  }
  spec {
    replicas = 2
    selector { match_labels = { app = var.project_name } }
    template {
      metadata { labels = { app = var.project_name } }
      spec {
        container {
          name  = "app"
          image = var.image_uri
          port { container_port = 7860 }
          env_from {
            secret_ref { name = var.openai_secret_name }
          }
          resources {
            requests = { cpu = "250m", memory = "512Mi" }
            limits   = { cpu = "500m", memory = "1Gi" }
          }
          readiness_probe {
            http_get {
              path = "/"
              port = 7860
            }
            initial_delay_seconds = 15
          }
          liveness_probe {
            http_get {
              path = "/"
              port = 7860
            }
            initial_delay_seconds = 45
          }
        }
      }
    }
  }
}
resource "kubernetes_service_v1" "app" {
  metadata {
    name      = var.project_name
    namespace = var.kubernetes_namespace
  }
  spec {
    selector = { app = var.project_name }
    type     = "LoadBalancer"
    port {
      port        = 80
      target_port = 7860
    }
  }
}
