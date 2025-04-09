terraform {
  backend "gcs" {
    bucket = "data-project2-terraform-state"
    prefix = "terraform/state"    
  }
}


