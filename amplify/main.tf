
resource "aws_amplify_app" "example" {
  name         = "mi-app-amplify"
  repository   = "https://github.com/nicolasli1/ANV3-229"
  oauth_token  = var.oauth_token
  access_token = var.access_token
  description  = "Una aplicación desplegada con Amplify para desarrollo."
  platform     = "WEB"
  build_spec   = file("build_spec.yml")

  auto_branch_creation_config {
    enable_auto_build = true
    enable_basic_auth = false

    environment_variables = {
      "BRANCH_ENV_VAR" = "valor"
    }
  }

  tags = {
    Name        = "mi-app-amplify"
    Environment = "desarrollo"
  }
}

# Define la rama principal
resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.example.id
  branch_name = "main"

  # Configuración opcional
  enable_auto_build = true
  enable_basic_auth = false
}
