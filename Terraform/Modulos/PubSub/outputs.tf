output "topic_id" {
  value = google_pubsub_topic.data_events.name
}

output "subscription_id" {
  value = google_pubsub_subscription.data_events_sub.name
}

output "topic_name" {
  description = "Nombre del tópico de Pub/Sub"
  value       = google_pubsub_topic.data_events.name
}
