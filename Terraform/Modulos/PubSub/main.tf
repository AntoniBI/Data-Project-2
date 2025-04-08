resource "google_pubsub_topic" "data_events" {
  name = "emergencias_events"
}

resource "google_pubsub_subscription" "data_events_sub" {
  name  = "${google_pubsub_topic.data_events.name}-sub"
  topic = google_pubsub_topic.data_events.name
}