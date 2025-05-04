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
  default = "europe-southwest1"
}

variable "service_name" {
  type = string
  default = "str-streamlit"
}

variable "image_url" {
  type = string
  default = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest"
}

