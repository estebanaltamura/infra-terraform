variable "aws_region" {
  description = "Región de AWS"
  type        = string
}

variable "ami_id" {
  description = "ID de la imagen AMI para la EC2"
  type        = string
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
}

variable "key_name" {
  description = "Nombre del par de claves para acceder por SSH"
  type        = string
}

variable "security_group_id" {
  description = "ID del Security Group para la instancia"
  type        = string
}



variable "ssh_private_key_path" {
  description = "Ruta local al archivo de clave privada para conexión SSH"
  type        = string
}

variable "ecr_base_url" {
  description = "URL base del repositorio de imágenes en ECR"
  type        = string
}

variable "ecr_registry" {
  description = "URL base del registry ECR"
  type        = string
}

variable "environment" {
  description = "Nombre del desarrollador que lanza la instancia"
  type        = string
}

variable "services_to_deploy" {
  type = list(string)
}

variable "available_services" {
  description = "Lista de servicios disponibles"
  type = list(string)
}





