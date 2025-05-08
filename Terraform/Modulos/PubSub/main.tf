provider "google" {
  project = var.project_id
  region  = var.region
}


resource "google_service_account" "pubsub_service_account" {
  account_id   = "pubsub-service-account"
  display_name = "Pub/Sub Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.pubsub_service_account.email}"
}


resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pubsub_service_account.email}"
}

resource "google_pubsub_topic" "data_events" {
  name = "emergencias_events"
}

resource "google_pubsub_subscription" "data_events_sub" {
  name  = "${google_pubsub_topic.data_events.name}-sub"
  topic = google_pubsub_topic.data_events.name
}

resource "google_pubsub_topic" "ubi_autos" {
  name = "emergencias_ubi_autos"
}

resource "google_pubsub_subscription" "ubi_autos_sub" {
  name="${google_pubsub_topic.ubi_autos.name}-sub"
  topic=google_pubsub_topic.ubi_autos.name 
}

resource "google_pubsub_topic" "no_matched" {
  name = "no_matched"
}

resource "google_pubsub_subscription" "no_matched" {
  name  = "${google_pubsub_topic.no_matched.name}-sub"
  topic = google_pubsub_topic.no_matched.name
}



