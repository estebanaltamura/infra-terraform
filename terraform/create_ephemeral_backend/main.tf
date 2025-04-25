provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "dev_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [var.security_group_id]

  tags = {
    Name = "${var.environment}.${formatdate("YYYY-MM-DD", timestamp())}"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -e

    # ─── Actualizar sistema ───────────────────────────────────────
    apt-get update -y
    apt-get upgrade -y

    # ─── Instalar Docker ─────────────────────────────────────────
    apt-get install -y docker.io curl
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    # ─── Instalar Docker Compose ─────────────────────────────────
    curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    # ─── Exportar variables de entorno para docker-compose ───────
    export ENVIRONMENT="${var.environment}"
    export ECR_REGISTRY="${var.ecr_registry}"

    # ─── Generar docker-compose.yml dinámico ─────────────────────
    APP_DIR="/home/ubuntu/app"
    mkdir -p "$${APP_DIR}"
    cat <<EOC > "$${APP_DIR}/docker-compose.yml"
    version: '3.8'
    services:
    %{ for svc in var.services_to_deploy ~}
      $${svc}:
        image: ${var.ecr_registry}/images/$${svc}
        restart: always
        environment:
          - ENVIRONMENT=$${ENVIRONMENT}
    %{ endfor ~}
    EOC

    chown -R ubuntu:ubuntu "$${APP_DIR}"

    # ─── Login a ECR y levantar contenedores ──────────────────────
    aws ecr get-login-password --region ${var.aws_region} \
      | docker login --username AWS --password-stdin ${var.ecr_registry}

    cd "$${APP_DIR}"
    docker-compose up -d
  EOF
}

output "instance_id" {
  value = aws_instance.dev_instance.id
}

output "public_ip" {
  value = aws_instance.dev_instance.public_ip
}
