# resource "null_resource" "docker_build" {
#   provisioner "local-exec" {
#     command = <<EOL
#       docker build --platform=linux/amd64 -t gen_ubi .
#       docker tag gen_ubi europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
#       docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
#     EOL
#   }
# }

# resource "google_cloud_run_v2_job" "run_job" {
#   name     = "str-image-job-generador-ubicaciones"
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
#     command = "gcloud run jobs execute str-image-job-generador-ubicaciones --region=europe-southwest1 --project=splendid-strand-452918-e6"
#   }

#   depends_on = [google_cloud_run_v2_job.run_job]
# }


# Crear la Service Account específica para este job
resource "google_service_account" "ubicacion_job_sa" {
  account_id   = "str-ubicacion-job-sa"
  display_name = "SA for Ubicación Generator Job"
  project      = var.project_id
}

# Darle permisos para invocar otros servicios de Cloud Run (como la API)
resource "google_project_iam_member" "ubicacion_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.ubicacion_job_sa.email}"
}

# Build y push de imagen Docker
resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t gen_ubi .
      docker tag gen_ubi europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-2/str-ubicaciones:latest
    EOL
  }
}

# Crear el Job de Cloud Run con la cuenta de servicio asociada
resource "google_cloud_run_v2_job" "run_job" {
  name     = "str-image-job-generador-ubicaciones"
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

      # Asociar la Service Account personalizada
      service_account = google_service_account.ubicacion_job_sa.email
      timeout         = "3600s"
      max_retries     = 3
    }
  }

  depends_on = [
    null_resource.docker_build,
    google_service_account.ubicacion_job_sa,
    google_project_iam_member.ubicacion_run_invoker
  ]
}

# Ejecutar el Job
resource "null_resource" "execute_run_job" {
  provisioner "local-exec" {
    command = "gcloud run jobs execute str-image-job-generador-ubicaciones --region=${var.region} --project=${var.project_id}"
  }

  depends_on = [google_cloud_run_v2_job.run_job]
}
