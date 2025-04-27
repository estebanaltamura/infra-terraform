import os
import subprocess
import boto3
import shutil

# Configuraciones comunes
AWS_REGION = "eu-north-1"
AWS_ACCOUNT_ID = "343668618236"
ECR_BASE_URL = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
SERVICES = ["service1", "service2", "service3"]

# Dockerfile base para todos los servicios
dockerfile_content = '''
FROM python:3.9-slim

RUN pip install flask

WORKDIR /app

COPY app.py app.py

CMD ["python", "app.py"]
'''

# Template del app.py
app_template = '''
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "{service_name}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
'''

def run(cmd, cwd=None):
    print(f"\n\033[92m$ {cmd}\033[0m")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def create_repository_if_not_exists(service_name):
    repo_name = f"images/{service_name}"
    ecr_client = boto3.client("ecr", region_name=AWS_REGION)
    try:
        response = ecr_client.create_repository(
            repositoryName=repo_name,
            imageTagMutability="MUTABLE",
            imageScanningConfiguration={"scanOnPush": False},
            encryptionConfiguration={"encryptionType": "AES256"}
        )
        print(f"\033[92mRepositorio creado: {repo_name}\033[0m")
    except ecr_client.exceptions.RepositoryAlreadyExistsException:
        print(f"\033[93mRepositorio ya existe: {repo_name}\033[0m")
    except Exception as e:
        print(f"\033[91mError creando repositorio {repo_name}: {e}\033[0m")

def main():
    # 1. Login a ECR
    print("Login a ECR...")
    run(f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {ECR_BASE_URL}")

    # 2. Crear repositorios si no existen
    for service in SERVICES:
        create_repository_if_not_exists(service)

    # 3. Crear carpetas y construir imágenes
    for service in SERVICES:
        print(f"\nConstruyendo {service}...")

        os.makedirs(service, exist_ok=True)

        # Crear Dockerfile
        with open(f"{service}/Dockerfile", "w") as f:
            f.write(dockerfile_content)

        # Crear app.py
        with open(f"{service}/app.py", "w") as f:
            f.write(app_template.format(service_name=service))

        # Build la imagen
        image_tag = f"{service}:latest"
        run(f"docker build -t {image_tag} .", cwd=service)

        # Taggear para ECR
        ecr_tag = f"{ECR_BASE_URL}/images/{service}:latest"
        run(f"docker tag {image_tag} {ecr_tag}")

        # Push a ECR
        print(f"Pusheando {service} a ECR...")
        run(f"docker push {ecr_tag}")

        # Eliminar imágenes locales
        print(f"Eliminando imagenes locales de {service}...")
        run(f"docker rmi {image_tag}")
        run(f"docker rmi {ecr_tag}")   

        # Eliminar carpeta local
        print(f"Eliminando carpeta temporal {service}/...")
        shutil.rmtree(service)

    print("\n\033[94mTodo terminado con éxito!\033[0m")
        
        
        
        
if __name__ == "__main__":
    main()


