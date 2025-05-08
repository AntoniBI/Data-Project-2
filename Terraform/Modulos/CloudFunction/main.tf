provider "google" {
  project = var.project_id 
  region  = var.region   
}

resource "google_pubsub_topic" "example_topic" {
  name = "streamlit"   
}


resource "google_storage_bucket" "example_bucket" {
  name          = "streamlit-source-bucket1314234"   
  location      = var.region                                 
  force_destroy = true                                  
}


resource "google_storage_bucket_object" "example_object" {
  name   = "function-source.zip"                       
  bucket = google_storage_bucket.example_bucket.name    
  source = "function-source.zip"           
}

resource "google_cloudfunctions_function" "example_function" {
  name        = "get_pubsub_message"
  region      = "europe-west1"                 
  description = "Cloud Function triggered by Pub/Sub topic"  
  runtime     = "python310"                            
  entry_point = "get_pubsub_message"                  
  available_memory_mb = 256                           

  
  source_archive_bucket = google_storage_bucket.example_bucket.name
  source_archive_object = google_storage_bucket_object.example_object.name

  
  event_trigger {
    event_type = "google.pubsub.topic.publish"        
    resource   = google_pubsub_topic.example_topic.id 
  }
}


resource "google_project_iam_member" "pubsub_subscriber" {
    role   = "roles/pubsub.subscriber"  
    member = "serviceAccount:${google_cloudfunctions_function.example_function.service_account_email}" 
    project= "splendid-strand-452918-e6" 
}
