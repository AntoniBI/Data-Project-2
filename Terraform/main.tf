# terraform {
#   backend "gcs" {
#     bucket = "data-project2-terraform-state"
#     prefix = "terraform/state"    
#   }
# }

resource "google_pubsub_topic" "data_events" {
  name = "poc_data2"
}

resource "google_pubsub_subscription" "data_events_sub" {
  name  = "${google_pubsub_topic.data_events.name}-sub"
  topic = google_pubsub_topic.data_events.name
}
