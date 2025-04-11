provider "google" {
    project = "splendid-strand-452918-e6"
    region  = "europe-southwest1"
    zone    = "europe-southwest1-a"
  
}
# 2. Habilitar API de Cloud Source Repositories
resource "google_project_service" "csr-apis" {
  service = "sourcerepo.googleapis.com"

  disable_dependent_services = true
  disable_on_destroy         = true
}

# 3. Crear el Repositorio en Cloud Source Repositories
resource "google_sourcerepo_repository" "cross-build-repo" {
  # Depende de que la API de CSR esté habilitada
  depends_on = [
    google_project_service.csr-apis
  ]
  name = "cross-build"
  # No se necesita la sección pubsub_configs
}

# 4. Habilitar API de Cloud Build
resource "google_project_service" "cloudbuild-apis" {
  service = "cloudbuild.googleapis.com"

  disable_dependent_services = true
  disable_on_destroy         = true
}

# 5. Crear el Disparador (Trigger) de Cloud Build
resource "google_cloudbuild_trigger" "cloudbuild-trigger" {
  # Define la fuente: el repositorio y la rama a observar
  trigger_template {
    branch_name = "master"                                         # Rama observada
    repo_name   = google_sourcerepo_repository.cross-build-repo.name # Repositorio observado
  }

  # Define qué archivo de configuración de compilación usar (debe existir en el repo)
  filename = "build-docker-image-trigger.yaml"

  # Especifica la cuenta de servicio que usará Cloud Build para ejecutar la compilación
  service_account = google_service_account.cloudbuild-runner-sa.id

  # Depende de que la API de Cloud Build y el repositorio existan,
  # y de que la cuenta de servicio para la ejecución exista.
  depends_on = [
    google_project_service.cloudbuild-apis,
    google_sourcerepo_repository.cross-build-repo,
    google_service_account.cloudbuild-runner-sa
  ]
}

# 6. Habilitar API de Container Registry (o Artifact Registry si lo prefieres)
# Necesario si tu archivo build-docker-image-trigger.yaml construye y sube imágenes Docker.
resource "google_project_service" "containerregistry-apis" {
  service = "containerregistry.googleapis.com"

  disable_dependent_services = true
  disable_on_destroy         = true
}

# --- Opcional pero Recomendado: Asignar Roles a la Cuenta de Servicio ---
# La cuenta de servicio de Cloud Build necesita permisos para hacer cosas,
# como subir artefactos a Container Registry/Artifact Registry, acceder a secretos, etc.

# Obtener el ID del proyecto actual (necesario para asignar roles a nivel de proyecto)
data "google_project" "current" {}

# Rol para permitir a Cloud Build ejecutar compilaciones
resource "google_project_iam_member" "cloudbuild_worker_role" {
  project = data.google_project.current.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.cloudbuild-runner-sa.email}"
}

# Rol para permitir subir imágenes a Google Container Registry (GCR)
# GCR usa buckets de Cloud Storage por debajo. 'roles/storage.admin' es amplio,
# podrías usar 'roles/storage.objectAdmin' si prefieres ser más específico.
resource "google_project_iam_member" "cloudbuild_gcr_pusher_role" {
  project = data.google_project.current.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild-runner-sa.email}"
}

# Rol para permitir a la cuenta de servicio usar recursos (opcional, depende de tu build)
# resource "google_project_iam_member" "cloudbuild_service_account_user_role" {
#   project = data.google_project.current.project_id
#   role    = "roles/iam.serviceAccountUser"
#   member  = "serviceAccount:${google_service_account.cloudbuild-runner-sa.email}"
# }