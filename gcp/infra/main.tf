provider "google" {
    project = "grounded-primer-436816-b5"
    region = "us-central1"
    credentials = file("credentials.json")
}

resource "google_bigquery_dataset" "default" {
  dataset_id                  = "DatasetCurso"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "EU"
  default_table_expiration_ms = 3600000

  labels = {
    env = "default"
  }
}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = "Estudiantes-curso"
  deletion_protection = false


  labels = {
    env = "default"
  }

  schema = <<EOF
[
  {
    "name": "id",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "un id"
  },
  {
    "name": "Nombre",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "el nombre"
  }
]
EOF

}


resource "google_storage_bucket" "bucket" {
  name     = "bucket-clase-gcp-72348901536247590"
  location = "US"
}

resource "google_storage_bucket_object" "Lecturabigquery" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = "../backend/lectura-bigquery/index.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "Lectura-bigquery"
  description = "My function"
  runtime     = "python310"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.Lecturabigquery.name
  trigger_http          = true
  entry_point           = "hello_http"
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

######################

resource "google_storage_bucket_object" "Escriturabigquery" {
  name   = "index2.zip"
  bucket = google_storage_bucket.bucket.name
  source = "../backend/escritura-bigquery/index2.zip"
}

resource "google_cloudfunctions_function" "function2" {
  name        = "Escritura-bigquery"
  description = "My function"
  runtime     = "python310"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.Escriturabigquery.name
  trigger_http          = true
  entry_point           = "hello_http"
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker2" {
  project        = google_cloudfunctions_function.function2.project
  region         = google_cloudfunctions_function.function2.region
  cloud_function = google_cloudfunctions_function.function2.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}