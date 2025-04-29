terraform {
  backend "gcs" {
    bucket = "data-project2-terraform-state"
    prefix = "terraform/state"    
  }
}

module "artifact_registry" {
  source     = "./Modulos/ArtifactRegistry"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
}

module "bigquery" {
  source     = "./Modulos/Bigquery"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
}

module "pubsub" {
  source     = "./Modulos/pubsub"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
}

# module "cloud_run_service" {
#   source       = "./Modulos/cloud_run_service"
#   project_id   = "splendid-strand-452918-e6"
#   region       = "europe-southwest1"
#   service_name = "str-service"
#   image_url    = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest"
# }