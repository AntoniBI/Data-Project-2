variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
  default = "splendid-strand-452918-e6"
}

variable "region" {
  description = "Región de GCP donde se desplegarán los recursos"
  type        = string
  default = "europe-west1"
}
