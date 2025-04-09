variable "project_id" {
  default = "splendid-strand-452918-e6"
}

variable "region" {
  default = "europe-southwest1"
}

variable "db_user" {
  default = "admin"
}

variable "db_password" {
  default = "admin123"
  sensitive = true
}

variable "db_name" {
  default = "coches_emergencia_db"
}
