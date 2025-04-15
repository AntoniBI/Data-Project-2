terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "data-project2-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Crear una cuenta de servicio para Grafana
resource "google_service_account" "grafana_sa" {
  account_id   = "grafana-service-account"
  display_name = "Service Account for Grafana"
}

# Asignar permisos a la cuenta de servicio para BigQuery
resource "google_project_iam_member" "grafana_bigquery_access" {
  role   = "roles/bigquery.viewer"
  member = "serviceAccount:${google_service_account.grafana_sa.email}"
}

# Crear un repositorio en Artifact Registry para almacenar la imagen de Docker
resource "google_artifact_registry_repository" "grafana_repo" {
  format       = "DOCKER"
  location     = var.region
  repository_id = "grafana-repo"
}

# Subir la imagen de Docker a Artifact Registry
resource "null_resource" "push_grafana_image" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/grafana-repo/grafana:latest ./Grafana &&
      docker push ${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/grafana-repo/grafana:latest
    EOT
  }
}

# Desplegar Grafana en Cloud Run
resource "google_cloud_run_service" "grafana" {
  name     = "grafana"
  location = var.region

  template {
    spec {
      containers {
        image = "${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/grafana-repo/grafana:latest"
        ports {
          container_port = 3000
        }
        env {
          name  = "GF_SECURITY_ADMIN_USER"
          value = "admin"
        }
        env {
          name  = "GF_SECURITY_ADMIN_PASSWORD"
          value = "admin"
        }
      }
      service_account_name = google_service_account.grafana_sa.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Permitir acceso público a Grafana
resource "google_cloud_run_service_iam_member" "grafana_invoker" {
  service = google_cloud_run_service.grafana.name
  location = google_cloud_run_service.grafana.location
  role = "roles/run.invoker"
  member = "allUsers"
}