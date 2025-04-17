

resource "google_sql_database_instance" "emergencias" {
  name             = "recursos"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    availability_type = "ZONAL"
    disk_size       = 100 
    # deletion_protection = false

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "public-access"
        value = "0.0.0.0/0"
      }
    }
  }
  lifecycle {
    prevent_destroy = false
  }
}


resource "google_sql_database" "vehiculos" {
  name     = var.db_name
  instance = google_sql_database_instance.emergencias.name
}

resource "google_sql_user" "usuario" {
  name     = var.db_user
  instance = google_sql_database_instance.emergencias.name
  password = var.db_password
}

resource "null_resource" "init_sql" {
  provisioner "local-exec" {
    command = "psql -h ${google_sql_database_instance.emergencias.public_ip_address} --username=${var.db_user} -d ${var.db_name} -p 5432 -f init.sql"
    environment = {
      PGPASSWORD = var.db_password
    }
    interpreter = ["PowerShell", "-Command"]
  }

  depends_on = [
    google_sql_database.vehiculos,
    google_sql_user.usuario
  ]
}

