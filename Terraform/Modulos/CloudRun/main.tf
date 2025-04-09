provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}
resource "google_cloud_run_v2_job" "init_db" {
  name     = "my-python-app"
  location = var.region

  template {
    template {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/my-python-app-repo/my-python-app"
        env {
          name  = "DB_HOST"
          value = "34.175.169.238"
        }

        env {
          name  = "DB_USER"
          value = var.db_user
        }

        env {
          name  = "DB_PASSWORD"
          value = var.db_password
        }

        env {
          name  = "DB_NAME"
          value = var.db_name
        }

        
      }
    }
  }
}
