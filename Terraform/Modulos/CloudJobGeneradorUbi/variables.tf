variable "api_url" {
  default ="https://str-service-puifiielba-no.a.run.app"
}

variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
  default = "splendid-strand-452918-e6"
}

variable "region" {
  description = "Región de GCP donde se desplegarán los recursos"
  type        = string
  default = "europe-southwest"
}

variable "service_name" {
  description = "Nombre del job o servicio de Cloud Run"
  type        = string
  default = "str-ubicaciones"
}

variable "image_url" {
  description = "URL de la imagen en Artifact Registry"
  type        = string
  default = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest"
}