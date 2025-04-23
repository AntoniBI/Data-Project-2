# resource "google_artifact_registry_repository" "my_repo" {
#   location      = "europe-southwest1"
#   repository_id = "data-project-repo"
#   description   = "Repository for data project"
#   format        = "DOCKER"


# }

# resource "null_resource" "docker_build" {
#   provisioner "local-exec" {
#     command = "docker build --platform=linux/amd64 -t streamlit . && docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image:latest && docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image:latest"

#   }

#   depends_on = [google_artifact_registry_repository.my_repo]
# }

# resource "google_cloud_run_service" "run-streamlit" {
#   name     = "str-image-web-streamlit"
#   location = "europe-southwest1"

#   template {
#     spec {
#       containers {
#         image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image"

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


# }


# Repositorio de Artifact Registry para almacenar imágenes Docker
resource "google_artifact_registry_repository" "my_repo" {
  location      = "europe-southwest1"
  repository_id = "data-project-repo"
  description   = "Repository for data project"
  format        = "DOCKER"
}

# Proceso de construcción de la imagen Docker
resource "null_resource" "docker_build" {
  provisioner "local-exec" {
    command = <<EOL
      docker build --platform=linux/amd64 -t streamlit .
      docker tag streamlit europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image:latest
      docker push europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image:latest
    EOL
  }

  depends_on = [google_artifact_registry_repository.my_repo]
}

# Servicio de Cloud Run para desplegar la aplicación Streamlit
resource "google_cloud_run_service" "run-streamlit" {
  name     = "str-image-web-streamlit"
  location = "europe-southwest1"

  template {
    spec {
      containers {
        # Usa la imagen con la etiqueta latest
        image = "europe-southwest1-docker.pkg.dev/splendid-strand-452918-e6/data-project-repo/str-image:latest"
        
        # Definición de variables de entorno (si las necesitas)
        env {
          name  = "api_url"
          value = var.api_url
        }
        
        # Puertos para exponer la aplicación
        ports {
          container_port = 8502
        }
      }
    }
  }

  # Dependencia para asegurarse que la imagen se haya construido antes de desplegar el servicio
  depends_on = [null_resource.docker_build]
}


# Comando para permitir invocaciones no autenticadas en el servicio de Cloud Run
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


