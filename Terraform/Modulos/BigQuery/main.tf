provider "google" {
    project = var.project_id
    region  = var.region
    zone    = "europe-southwest1-a"
  
}

resource "google_service_account" "bigquery_sa" {
  account_id   = "bigquery-sa"
  display_name = "BigQuery Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "bigquery_sa_member" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

resource "google_bigquery_dataset" "emergencia-eventos" {
  dataset_id  = "emergencia_eventos"
  project     = var.project_id
  location    = "europe-southwest1"
}

resource "google_bigquery_table" "emergencias" {
  dataset_id = google_bigquery_dataset.emergencia-eventos.dataset_id
  table_id   = "emergencias-macheadas"

  schema = <<EOF
[
  {"name": "evento_id", "type": "STRING"},
  {"name": "servicio_evento", "type": "STRING"},
  {"name": "lat_evento", "type": "FLOAT64"},
  {"name": "lon_evento", "type": "FLOAT64"},
  {"name": "timestamp_evento", "type": "TIMESTAMP"},
  {"name": "tipo", "type": "STRING"},
  {"name": "descapacidad", "type": "STRING"},
  {"name": "nivel_emergencia", "type": "STRING"},
  {"name": "recurso_id", "type": "STRING"},
  {"name": "servicio_recurso", "type": "STRING"},
  {"name": "edad", "type": "INTEGER"},
  {"name": "lat_recurso", "type": "FLOAT64"},
  {"name": "lon_recurso", "type": "FLOAT64"},
  {"name": "timestamp_ubicacion", "type": "TIMESTAMP"},
  {"name": "coeficiente", "type": "FLOAT64"},
  {"name": "coeficiente_seleccionado", "type": "FLOAT64"},
  {"name": "tiempo_total", "type": "FLOAT64"},
  {"name": "tiempo_respuesta", "type": "FLOAT64"},
  {"name": "distancia_recorrida" , "type": "FLOAT64"},
  {"name": "disponible_en" , "type": "TIMESTAMP"}
]
EOF
}

resource "google_bigquery_table" "emergencias-no-macheadas" {
  dataset_id = google_bigquery_dataset.emergencia-eventos.dataset_id
  table_id   = "emergencias-no-macheadas"

  schema = <<EOF
[
  {"name": "evento_id", "type": "STRING"},
  {"name": "servicio_evento", "type": "STRING"},
  {"name": "lat_evento", "type": "FLOAT64"},
  {"name": "lon_evento", "type": "FLOAT64"},
  {"name": "tipo", "type": "STRING"},
  {"name": "discapacidad", "type": "STRING"},
  {"name": "nivel_emergencia", "type": "STRING"},
  {"name": "edad", "type": "INTEGER"},
  {"name": "timestamp_evento", "type": "TIMESTAMP"},
  {"name": "coeficientes", "type": "FLOAT64"},
  {"name": "no_mached_count", "type": "INTEGER"}
]
EOF
}





