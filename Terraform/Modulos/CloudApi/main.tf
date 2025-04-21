resource "google_artifact_registry_repository" "my_repo" {
  location      = "europe-southwest1"
  repository_id = "data-project-repo-3"
  description   = "Repository for data project"
  format        = "DOCKER"


}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = "docker build --platform linux/amd64 -t api . && docker tag api europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-3/str-image:latest && docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-3/str-image:latest"

  }

  depends_on = [google_artifact_registry_repository.my_repo]
}

resource "google_cloud_run_service" "default" {
  name     = "str-service"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo-3/str-image:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [null_resource.docker_build]
}


