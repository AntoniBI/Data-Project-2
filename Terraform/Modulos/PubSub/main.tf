provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "data_events" {
  name = "emergencias_events2"
}

resource "google_pubsub_subscription" "data_events_sub" {
  name  = "${google_pubsub_topic.data_events.name}-sub"
  topic = google_pubsub_topic.data_events.name
}

resource "google_pubsub_topic" "ubi_autos" {
  name = "emergencias_ubi_autos2"
}

resource "google_pubsub_subscription" "ubi_autos_sub" {
  name="${google_pubsub_topic.ubi_autos.name}-sub"
  topic=google_pubsub_topic.ubi_autos.name 
}

resource "google_pubsub_topic" "no_matched" {
  name = "no_matched2"
}

resource "google_pubsub_subscription" "no_matched" {
  name  = "${google_pubsub_topic.no_matched.name}-sub"
  topic = google_pubsub_topic.no_matched.name
}