# resource "null_resource" "docker_build" {
#   provisioner "local-exec" {
#     command = <<EOL
#       docker build --platform=linux/amd64 -t streamlit .
#       docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
#       docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
#     EOL
#   }
# }

# resource "google_cloud_run_service" "run-streamlit" {
#   name     = "str-image-web-streamlit"
#   location = var.region

#   template {
#     spec {
#       containers {
#         image = var.image_url
        
#         env {
#           name  = "api_url"
#           value = var.api_url
#         }

#         ports {
#           container_port = 8502
#         }
#       }
#     }
#   }

#   depends_on = [null_resource.docker_build]
# }

# resource "null_resource" "allow_unauthenticated_access" {
#   provisioner "local-exec" {
#     command = <<EOL
#       gcloud run services add-iam-policy-binding str-image-web-streamlit \
#         --region=europe-southwest1 \
#         --member="allUsers" \
#         --role="roles/run.invoker" \
#         --project=splendid-strand-452918-e6
#     EOL
#   }

#   depends_on = [google_cloud_run_service.run-streamlit]
# }





resource "google_service_account" "streamlit_invoker" {
  account_id   = "streamlit-invoker-sa"
  display_name = "Streamlit Invoker Service Account"
}


resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t streamlit ${path.module}
      docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-streamlit:latest
    EOL
  }
}


resource "google_cloud_run_service" "run-streamlit" {
  name     = "str-image-web-streamlit"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.streamlit_invoker.email

      containers {
        image = var.image_url

        env {
          name  = "api_url"
          value = var.api_url
        }

        ports {
          container_port = 8502
        }
      }
    }
  }

  depends_on = [null_resource.docker_build]
}


resource "null_resource" "allow_unauthenticated_access" {
  provisioner "local-exec" {
    command = <<EOL
      gcloud run services add-iam-policy-binding str-image-web-streamlit \
        --region=europe-southwest1 \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --project=splendid-strand-452918-e6
    EOL
  }
depends_on = [google_cloud_run_service.run-streamlit]
}

# resource "google_cloud_run_service_iam_member" "allow_streamlit_to_call_api" {
#   location = "europe-southwest1"
#   service  = "str-service"
#   role     = "roles/run.invoker"
#   member   = "serviceAccount:${google_service_account.streamlit_invoker.email}"

# }
