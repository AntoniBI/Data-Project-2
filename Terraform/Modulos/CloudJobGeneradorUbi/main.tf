resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t gen_ubi .
      docker tag gen_ubi europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
    EOL
  }
}

resource "google_cloud_run_v2_job" "run_job" {
  name     = "str-image-job-generador-ubicaciones"
  location = "europe-southwest1"
  project  = "splendid-strand-452918-e6"

  template {
    template {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest"

        env {
          name  = "api_url"
          value = var.api_url
        }
      }

      timeout     = "3600s"
      max_retries = 3
    }
  }

  depends_on = [null_resource.docker_build]
}

resource "null_resource" "execute_run_job" {
  provisioner "local-exec" {
    command = "gcloud run jobs execute str-image-job-generador-ubicaciones --region=europe-southwest1 --project=splendid-strand-452918-e6"
  }

  depends_on = [google_cloud_run_v2_job.run_job]
}
