resource "google_cloud_run_service" "run-grafana" {
  name     = "grafana"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = " europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image@sha256:c58c75ea983420b652da957a5f3db5541aa32a3c1d7ca1b5e489a4200d4bdc98"

        ports {
          container_port = 3000
        }

        env {
          name  = "PORT"
          value = "3000"
        }
      }
    }
  }
}

resource "google_cloud_run_service_iam_policy" "public_access" {
  service     = google_cloud_run_service.run-grafana.name
  location    = google_cloud_run_service.run-grafana.location
  policy_data = data.google_iam_policy.public_iam_policy.policy_data
}

data "google_iam_policy" "public_iam_policy" {
  binding {
    role    = "roles/run.invoker"
    members = ["allUsers"]
  }
}
