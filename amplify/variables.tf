variable "oauth_token" {
  description = "El token OAuth para autenticación"
  type        = string
  default     = "secreto"  # Puedes poner un valor por defecto si lo deseas
}

variable "access_token" {
  description = "El token de acceso para API"
  type        = string
  default     = "secreto"  # Igual aquí
}
