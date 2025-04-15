#Ejemplo crear tabla en bigquery. Hay que crear esquemas
provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}

# BigQuery Resources
resource "google_bigquery_dataset" "emergencia-eventos" {
  dataset_id  = "emergencia_eventos"
  project     = var.project_id
  location    = "europe-southwest1"
}

resource "google_bigquery_table" "emergencias" {
  dataset_id = google_bigquery_dataset.emergencia-eventos.dataset_id
  table_id   = "emergencias-macheada"

  schema = <<EOF
[
  {"name": "evento_id", "type": "STRING"},
  {"name": "servicio_evento", "type": "STRING"},
  {"name": "lat_evento", "type": "FLOAT64"},
  {"name": "lon_evento", "type": "FLOAT64"},
  {"name": "timestamp_evento", "type": "TIMESTAMP"},
  {"name": "recurso_id", "type": "STRING"},
  {"name": "servicio_recurso", "type": "STRING"},
  {"name": "lat_recurso", "type": "FLOAT64"},
  {"name": "lon_recurso", "type": "FLOAT64"},
  {"name": "timestamp_ubicacion", "type": "TIMESTAMP"}
]
EOF
}
