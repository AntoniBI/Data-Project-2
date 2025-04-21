resource "google_artifact_registry_repository" "my_repo" {
  location      = "europe-southwest1"
  repository_id = "data-project-repo-job"
  description   = "Repository for data project"
  format        = "DOCKER"


}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = "docker build--platform=linux/amd64 -t gen_app . && docker tag gen_app europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-job/str-image:latest && docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-job/str-image:latest"

  }

  depends_on = [google_artifact_registry_repository.my_repo]
}

resource "google_cloud_run_v2_job" "run_job" {
  name     = "str-image-job-generador-app"
  location = "europe-southwest1"

  template {
    template {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-job/str-image:latest"
      }

      # Configura si tu script necesita alguna env var o recurso
      timeout     = "3600s"
      max_retries = 3
    }
  }

  depends_on = [null_resource.docker_build]
}

resource "null_resource" "execute_run_job" {
  provisioner "local-exec" {
    command = "gcloud run jobs execute str-image-job --region=europe-southwest1 --project=splendid-strand-452918-e6"
  }

  depends_on = [google_cloud_run_v2_job.run_job]
}

