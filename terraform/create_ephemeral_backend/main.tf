############################################
# 1) VARIABLES LOCALES – BLOQUES DE SCRIPT #
############################################
locals {
  # -- 0. Cabecera / flags -----------------
  header = <<-BASH
#!/bin/bash
set -xe   # -x: debug, -e: aborta al primer fallo
  BASH

  # -- 1. Actualización del sistema --------
  update_system = <<-BASH
# 1) Actualizar sistema
apt-get update -y
apt-get upgrade -y
  BASH

  # -- 2. Instalación de Docker ------------
  install_docker = <<-BASH
# 2) Instalar Docker y dependencias
apt-get install -y docker.io curl
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu
  BASH

  # -- 3. Instalación de Docker Compose ----
  install_compose = <<-BASH
# 3) Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
  BASH

# -- 3.5 Instalar AWS CLI -------------------
install_awscli = <<-BASH
# 3.5) Instalar AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
apt-get install -y unzip
unzip awscliv2.zip
./aws/install
  BASH

  # -- 4. Generar docker-compose.yml -------
  generate_compose = <<-BASH
# 4) Generar docker-compose.yml
APP_DIR="/home/ubuntu/app"
mkdir -p "$APP_DIR"

cat <<'EOC' > "$APP_DIR/docker-compose.yml"
version: '3.8'
services:
%{ for svc in var.services_to_deploy ~}
  ${svc}:
    image: ${var.ecr_registry}/images/${svc}
    restart: always
    environment:
      - ENVIRONMENT=${var.environment}
%{ endfor ~}
EOC

chown -R ubuntu:ubuntu "$APP_DIR"
  BASH

  # -- 5. Login en ECR y despliegue --------
  ecr_deploy = <<-BASH
# 5) Login a ECR y desplegar servicios como usuario ubuntu
runuser -l ubuntu -c 'aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${var.ecr_registry}'

cd "$APP_DIR"
runuser -l ubuntu -c 'cd $APP_DIR && docker-compose up -d'
  BASH
}

###############################
# 2) RECURSO EC2 CON USERDATA #
###############################
resource "aws_iam_role" "ecr_role" {
  name = var.iam_role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "ecr_instance_profile" {
  name = var.iam_instance_profile_name
  role = aws_iam_role.ecr_role.name
}

resource "aws_instance" "dev_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.ecr_instance_profile.name


  # Etiquetas separadas: más fáciles de filtrar en AWS
  tags = {
    Name = "Environment: ${var.environment} || Services: ${join(", ", var.services_to_deploy)}"
    Environment = var.environment
    Services    = join(", ", var.services_to_deploy)
  }

  # Unimos los bloques en el orden deseado
  user_data = join("\n", [
    local.header,
    local.update_system,
    local.install_docker,
    local.install_compose,
    local.install_awscli,
    local.generate_compose,
    local.ecr_deploy
  ])
}

############################################
# 3) ¿CÓMO USAR ESTE ENFOQUE?              #
############################################
# • Añadir/quitar pasos → solo editas el local correspondiente.
# • Reordenar pasos   → cambias el orden dentro del array de join().
# • Reutilizar bloques → puedes referenciarlos en otros recursos TF.
# • Plantillas más grandes → mueve cada bloque a un fichero y usa
#   templatefile() si prefieres mantenerlos fuera del .tf.

output "instance_id" {
  description = "ID de la instancia EC2 creada"
  value       = aws_instance.dev_instance.id
}

output "public_ip" {
  description = "IP pública de la instancia"
  value       = aws_instance.dev_instance.public_ip
}