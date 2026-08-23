resource "kubernetes_namespace" "terraform_demo" {
  metadata {
    name = "terraform-demo"
  }
}

resource "kubernetes_config_map" "task_api_config" {
  metadata {
    name      = "task-api-config"
    namespace = kubernetes_namespace.terraform_demo.metadata[0].name
  }
  data = {
    APP_ENV = "terraform-practice"
  }
}

resource "kubernetes_deployment" "task_api" {
  metadata {
    name      = "task-api"
    namespace = kubernetes_namespace.terraform_demo.metadata[0].name
    labels    = { app = "task-api" }
  }
  spec {
    replicas = 2
    selector {
      match_labels = { app = "task-api" }
    }
    template {
      metadata {
        labels = { app = "task-api" }
      }
      spec {
        container {
          name  = "task-api"
          image = "ghcr.io/mdaquib43/devops-practice-pipeline:latest"
          port {
            container_port = 8000
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.task_api_config.metadata[0].name
            }
          }
          env_from {
            secret_ref {
              name = kubernetes_secret.task_api_secret.metadata[0].name
            }
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 3
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "task_api" {
  metadata {
    name      = "task-api"
    namespace = kubernetes_namespace.terraform_demo.metadata[0].name
  }
  spec {
    selector = { app = "task-api" }
    port {
      port        = 80
      target_port = 8000
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_secret" "task_api_secret" {
  metadata {
    name      = "task-api-secret"
    namespace = kubernetes_namespace.terraform_demo.metadata[0].name
  }
  data = {
    username = "admin"
    password = "P4ssw0rd"
  }
}