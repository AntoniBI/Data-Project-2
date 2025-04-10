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
  table_id   = "emergencias"

  schema = <<EOF
[
  {"name": "id", "type": "INT64"},
  {"name": "servicio", "type": "STRING"},
  {"name": "tipo", "type": "STRING"},
  {"name": "edad", "type": "STRING"},
  {"name": "disc", "type": "STRING"},
  {"name": "nivel", "type": "STRING"},
  {"name": "lat", "type": "FLOAT64"},
  {"name": "lon", "type": "FLOAT64"}
]
EOF
}
