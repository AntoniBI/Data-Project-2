resource "google_artifact_registry_repository" "central_repo" {
  project       = "splendid-strand-452918-e6"
  location      = "europe-southwest1"
  repository_id = "data-project-2"
  description   = "Repository for data project"
  format        = "DOCKER"
}