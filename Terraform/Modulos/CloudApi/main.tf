# provider "google" {
#   project = var.project_id
#   region  = var.region
# }

resource "google_service_account" "cloud_run_service_account" {
  account_id   = "cloud-run-service-account"
  display_name = "Cloud Run Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cloud_run_service_account.email}"
}

resource "google_project_iam_member" "bigquery_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_service_account.email}"
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_service_account.email}"
}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform linux/amd64 -t api ${path.module}
      docker tag api europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest
    EOL
  }
}

resource "google_cloud_run_service" "default" {
  name     = "str-service"
  location = "europe-southwest1"

  template {
    spec {
      service_account_name = google_service_account.cloud_run_service_account.email

      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [null_resource.docker_build]
}

resource "null_resource" "allow_unauthenticated_access_api" {
  provisioner "local-exec" {
    command = <<EOL
      gcloud run services add-iam-policy-binding str-service \
        --region=europe-southwest1 \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --project=splendid-strand-452918-e6
    EOL
  }

  depends_on = [google_cloud_run_service.default]
}

