# resource "null_resource" "docker_build" {
#   provisioner "local-exec" {
#     command = <<EOL
#       docker build --platform=linux/amd64 -t gen_app .
#       docker tag gen_app europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-generator:latest
#       docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-generator:latest
#     EOL
#   }
# }

# resource "google_cloud_run_v2_job" "run_job" {
#   name     = "str-image-job-generador-emergencias"
#   location = var.region
#   project  = var.project_id

#   template {
#     template {
#       containers {
#         image = var.image_url

#         env {
#           name  = "api_url"
#           value = var.api_url
#         }
#       }

#       timeout     = "3600s"
#       max_retries = 3
#     }
#   }

#   depends_on = [null_resource.docker_build]
# }

# resource "null_resource" "execute_run_job" {
#   provisioner "local-exec" {
#     command = "gcloud run jobs execute str-image-job-generador-emergencias --region=europe-southwest1 --project=splendid-strand-452918-e6"
#   }

#   depends_on = [google_cloud_run_v2_job.run_job]
# }

# Crear la cuenta de servicio para el job de Cloud Run
resource "google_service_account" "run_job_service_account" {
  account_id   = "str-job-service-account"
  display_name = "Service Account for Cloud Run Job"
  project = var.project_id
}

# Asignar permisos de invocador de Cloud Run a la cuenta de servicio
resource "google_project_iam_member" "run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.run_job_service_account.email}"
}

# Asignar permisos de publisher de Pub/Sub a la cuenta de servicio (si el job publica en Pub/Sub)
resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.run_job_service_account.email}"
}

resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t gen_app .
      docker tag gen_app europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-generator:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-generator:latest
    EOL
  }
}


# Crear el Job de Cloud Run con la cuenta de servicio asociada
resource "google_cloud_run_v2_job" "run_job" {
  name     = "str-image-job-generador-emergencias"
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = var.image_url

        env {
          name  = "api_url"
          value = var.api_url
        }
      }

      # Asociar la cuenta de servicio al job de Cloud Run
      service_account = google_service_account.run_job_service_account.email
      timeout         = "3600s"
      max_retries     = 3
    }
  }

  depends_on = [null_resource.docker_build]
}

# Ejecutar el Job de Cloud Run
resource "null_resource" "execute_run_job" {
  provisioner "local-exec" {
    command = "gcloud run jobs execute str-image-job-generador-emergencias --region=europe-southwest1 --project=splendid-strand-452918-e6"
  }

  depends_on = [google_cloud_run_v2_job.run_job]
}

