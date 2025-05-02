resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t streamlit .
      docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
    EOL
  }
}

resource "google_cloud_run_service" "run-streamlit" {
  name     = "str-image-web-streamlit"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest"
        
        env {
          name  = "api_url"
          value = var.api_url
        }

        ports {
          container_port = 8502
        }
      }
    }
  }

  depends_on = [null_resource.docker_build]
}

resource "null_resource" "allow_unauthenticated_access" {
  provisioner "local-exec" {
    command = <<EOL
      gcloud run services add-iam-policy-binding str-image-web-streamlit \
        --region=europe-southwest1 \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --project=splendid-strand-452918-e6
    EOL
  }

  depends_on = [google_cloud_run_service.run-streamlit]
}

