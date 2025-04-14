output "public_ip" {
  value = google_sql_database_instance.emergencias.public_ip_address
}

