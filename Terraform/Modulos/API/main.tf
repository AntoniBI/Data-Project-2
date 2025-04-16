resource "google_artifact_registry_repository" "my_repo" {
  location      = "europe-southwest1"
  repository_id = "data-project-repo"
  description   = "Repository for data project"
  format        = "DOCKER"


}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = "docker build -t API . && docker tag API europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/API-image:latest && docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/API-image:latest"

  }

  depends_on = [google_artifact_registry_repository.my_repo]
}


