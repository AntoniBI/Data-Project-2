variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
  default     = "europe-southwest1"
}
