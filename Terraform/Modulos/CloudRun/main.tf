resource "google_cloud_run_service" "default" {
  name     = "streamlit"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/streamlit@sha256:7d0d127842795e50aa493b4e735346d0d0d61680c3822ed0511730ff5d606039"

        # Configurar el puerto de salida
        ports {
          container_port = 8502 # Cambia el puerto aquí si es necesario
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }


}