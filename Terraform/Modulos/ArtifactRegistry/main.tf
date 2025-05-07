resource "google_service_account" "artifact_registry_sa" {
  account_id   = "artifact-registry-sa"
  display_name = "Artifact Registry Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "artifact_registry_sa_member" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.artifact_registry_sa.email}"
}


resource "google_artifact_registry_repository" "central_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "data-project-2"
  description   = "Repository for data project"
  format        = "DOCKER"
}