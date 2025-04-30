variable "project_id" {
  type = string
  default = "splendid-strand-452918-e6"
}

variable "region" {
  type = string
  default = "europe-southwest1"
}

variable "service_name" {
  type = string
default = "str-service"
}

variable "image_url" {
  type = string
default = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-api:latest"
}
