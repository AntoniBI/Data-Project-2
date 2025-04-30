variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
  default     = "splendid-strand-452918-e6"
}

variable "region" {
  description = "Región de despliegue"
  type        = string
  default     = "europe-southwest1"
}

variable "service_name" {
  description = "Nombre del servicio de Cloud Run"
  type        = string
  default = "grafana-bq"
}

variable "api_url" {
  description = "URL de la API"
  type        = string
  default     = "https://str-service-puifiielba-no.a.run.app"
}

variable "image_url" {
  description = "URL de la imagen Docker"
  type        = string
  default     = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/grafana-bq:latest"
}
