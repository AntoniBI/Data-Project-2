provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}
resource "google_cloud_run_v2_service" "default" {
  name     = "cloudrun-service"
  location = "europe-southwest1"
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/splendid-strand-452918-e6/emergencia-app"
    }
  }
}

