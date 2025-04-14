variable "project_id" {
    description = "The GCP project ID"
    type        = string
    default     = "splendid-strand-452918-e6"
}
variable "region" {
  default = "europe-southwest1"
}
variable "db_name" {
  default = "recursos-emergencia"
}
variable "db_user" {
  default = "vehiculos"
}
variable "db_password" {
  default = "admin123"
}