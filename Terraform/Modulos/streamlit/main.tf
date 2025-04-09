provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}
resource "google_cloud_run_service" "sample_service" {
  name = "str-job-65485"
  location = "europe-southwest1"
  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/streamlit-repo/str-job"
        ports {
          container_port = 8080 
        }
      }
      timeout_seconds = 600 
    }
  }
}
