resource "google_cloud_run_service" "run-API" {
  name     = "str-image"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-1/str-image@sha256:2119e36b36e07dd504cf6a57ed3a2c7ed23cbc28011631a4b6ce8c06fa02d9ce"

   
        ports {
          container_port = 8082
        }
      }
    }
  }


}

resource "google_cloud_run_service_iam_policy" "public_access" {
  service = google_cloud_run_service.run-API.name
  location = google_cloud_run_service.run-API.location
  policy_data = data.google_iam_policy.public_iam_policy.policy_data
}

data "google_iam_policy" "public_iam_policy" {
  binding {
    role = "roles/run.invoker"
    members = ["allUsers"]
  }
}