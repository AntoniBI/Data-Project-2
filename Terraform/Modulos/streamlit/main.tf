resource "google_artifact_registry_repository" "my_repo" {
  location      = "europe-southwest1"
  repository_id = "data-project-repo"
  description   = "Repository for data project"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }
}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = "gcloud auth configure-docker europe-southwest1-docker.pkg.dev && docker build -t streamlit . && docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/streamlit:latest && docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/streamlit:v1.0"

  }

  depends_on = [google_artifact_registry_repository.my_repo]
}


