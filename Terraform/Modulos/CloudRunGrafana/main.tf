# resource "google_service_account" "grafana_sa" {
#   account_id   = "grafana-sa"
#   display_name = "Grafana Service Account"
# }

# resource "google_project_iam_member" "grafana_bigquery_viewer" {
#   project = var.project_id
#   role    = "roles/bigquery.dataViewer"
#   member  = "serviceAccount:${google_service_account.grafana_sa.email}"
# }

# resource "google_project_iam_member" "grafana_bigquery_jobuser" {
#   project = var.project_id
#   role    = "roles/bigquery.jobUser"
#   member  = "serviceAccount:${google_service_account.grafana_sa.email}"
# }

# resource "google_artifact_registry_repository" "grafana_repo" {
#   format       = "DOCKER"
#   location     = var.region
#   repository_id = "data-project-repo5"
# }


# resource "null_resource" "build_and_push_image" {
#   triggers = {
#     always_run = timestamp()
#   }

#   provisioner "local-exec" {
#     command = <<EOT
#       cd grafana && \
#       docker build --no-cache --platform=linux/amd64 -t grafana-bq . && \
#       docker tag grafana-bq ${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.grafana_repo.repository_id}/grafana-bq:latest && \
#       docker push ${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.grafana_repo.repository_id}/grafana-bq:latest
#     EOT
#   }
# }

# resource "google_cloud_run_service" "grafana" {
#   name     = "grafana"
#   location = var.region
#   depends_on = [null_resource.build_and_push_image]

#   template {
#     spec {
#       service_account_name = google_service_account.grafana_sa.email
#       containers {
#         image = "${google_artifact_registry_repository.grafana_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.grafana_repo.repository_id}/grafana-bq:latest"
#         ports {
#           container_port = 3000
#         }
#       }
#     }
#   }

#   traffic {
#     percent         = 100
#     latest_revision = true
#   }
# }


# resource "google_cloud_run_service_iam_policy" "grafana_public" {
#   location = google_cloud_run_service.grafana.location
#   service  = google_cloud_run_service.grafana.name

#   policy_data = data.google_iam_policy.grafana_invoker.policy_data
# }

# data "google_iam_policy" "grafana_invoker" {
#   binding {
#     role    = "roles/run.invoker"
#     members = ["allUsers"]
#   }
# }




resource "google_service_account" "grafana_sa" {
  account_id   = "grafana-sa"
  display_name = "Grafana Service Account"
}

resource "google_project_iam_member" "grafana_bigquery_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.grafana_sa.email}"
}

resource "google_project_iam_member" "grafana_bigquery_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.grafana_sa.email}"
}

resource "null_resource" "build_and_push_image" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOT
      cd grafana && \
      docker build --no-cache --platform=linux/amd64 -t grafana-bq . && \
      docker tag grafana-bq ${var.region}-docker.pkg.dev/${var.project_id}/data-project-2/grafana-bq:latest && \
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/data-project-2/grafana-bq:latest
    EOT
  }
}

resource "google_cloud_run_service" "grafana" {
  name     = "grafana"
  location = var.region
  depends_on = [null_resource.build_and_push_image]

  template {
    spec {
      service_account_name = google_service_account.grafana_sa.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/data-project-2/grafana-bq:latest"
        ports {
          container_port = 3000
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "grafana_public" {
  location = google_cloud_run_service.grafana.location
  service  = google_cloud_run_service.grafana.name

  policy_data = data.google_iam_policy.grafana_invoker.policy_data
}

data "google_iam_policy" "grafana_invoker" {
  binding {
    role    = "roles/run.invoker"
    members = ["allUsers"]
  }
}
