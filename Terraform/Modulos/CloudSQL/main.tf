provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}

resource "google_sql_database_instance" "postgres_instance" {
  name             = "data-project-2"
  database_version = "POSTGRES_14"
  region           = var.region
  # provisioner "local-exec" {
  #   command="PGPASSWORD=admin123 psql -f schema.sql -p 5432 -U admin coches_emergencia_db"
  # }

  settings {
    tier = "db-f1-micro"
    availability_type = "ZONAL"
    disk_size = 100 

    ip_configuration {
      ipv4_enabled    = true
      authorized_networks {
        name  = "public-acces"
        value = "0.0.0.0/0"  
      }
    }
  }
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_sql_user" "postgres_users" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}

resource "google_sql_database" "coches_emergencia_db" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres_instance.name
}

# resource "null_resource" "init_table" {
#   depends_on = [google_sql_database.default]
# }

