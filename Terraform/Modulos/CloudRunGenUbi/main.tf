resource "google_cloud_run_service" "run-streamlit" {
  name     = "str-image"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image@sha256:941d2822b13dfe75cbdfe1ce8c98f6e984082101e09a3511c849fcdebb0b3f3c"

   
        ports {
          container_port = 8502 
        }
      }
    }
  }


}

resource "google_cloud_run_service_iam_policy" "public_access" {
  service = google_cloud_run_service.run-streamlit.name
  location = google_cloud_run_service.run-streamlit.location
  policy_data = data.google_iam_policy.public_iam_policy.policy_data
}

data "google_iam_policy" "public_iam_policy" {
  binding {
    role = "roles/run.invoker"
    members = ["allUsers"]
  }
}