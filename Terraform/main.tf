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
  source     = "./Modulos/BigQuery"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
}

module "pubsub" {
  source     = "./Modulos/pubsub"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
}

module "cloudsql" {
  source     = "./Modulos/CloudSQL"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
  db_name    = "recursos-emergencia"
  db_user    = "vehiculos"
  db_password    = "admin123"
  
}
module "cloud_run_api" {
  source       = "./Modulos/CloudApi"
  project_id   = "splendid-strand-452918-e6"
  region       = "europe-southwest1"
  service_name = "str-service"
  image_url    = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest"


  depends_on = [module.pubsub]
}

module "cloud_run_streamlit" {
  source     = "./Modulos/CloudStreamlit"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
  service_name = "str-streamlit"
  api_url    = "https://str-service-puifiielba-no.a.run.app"
  image_url = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest"
}


module "cloud_run_job_generador" {
  source     = "./Modulos/CloudJobGeneradorApp"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
  service_name   = "str-image-job-generador-emergencias"
  api_url = "https://str-service-puifiielba-no.a.run.app"
  image_url  = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-generator:latest"
  
  depends_on = [module.cloudsql, module.pubsub, module.cloud_run_api]
  
}


module "cloud_run_job_ubicaciones" {
  source     = "./Modulos/CloudJobGeneradorUbi"  
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
  api_url = "https://str-service-puifiielba-no.a.run.app"
  service_name = "str-ubicaciones"
  image_url  = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest"

   depends_on = [module.cloudsql, module.pubsub, module.cloud_run_api]

}

module "cloud_run_grafana" {
  source     = "./Modulos/CloudRunGrafana"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-southwest1"
  service_name = "grafana-bq"
  api_url    = "https://str-service-puifiielba-no.a.run.app"
  image_url  = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/grafana-bq:latest"

  depends_on = [module.bigquery]
  
}

resource "google_cloud_run_service_iam_member" "allow_streamlit_to_call_api" {
  location = "europe-southwest1"
  service  = "str-service"
  role     = "roles/run.invoker"
  member   = "serviceAccount:${module.cloud_run_streamlit.streamlit_invoker_email}"

  depends_on = [
    module.cloud_run_api,
    module.cloud_run_streamlit]
}

module "cloud_function_pubsub" {
  source     = "./Modulos/CloudFunction"
  project_id = "splendid-strand-452918-e6"
  region     = "europe-west1"
}

