resource "google_artifact_registry_repository" "central_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "data-project-2"
  description   = "Repository for data project"
  format        = "DOCKER"
}