from fastapi import APIRouter, Request, Header, HTTPException
import os
import subprocess
import json


router = APIRouter()

def get_terraform_outputs(tf_path):
    output = subprocess.check_output(["terraform", "output", "-json"], cwd=tf_path)
    parsed = json.loads(output)
    return {
        "instance_id": parsed["instance_id"]["value"],
        "instance_ip": parsed["public_ip"]["value"]
    }

@router.post("/")
async def create_ephemeral_backend(request: Request):
    body = await request.json()

    
    # 1. Required keys
    required_fields = {"environment", "services_to_deploy"}
    missing = required_fields - set(body.keys())
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(sorted(missing))}"
        )

    print('llego')
    # 2. Type checks

    if not isinstance(body["environment"], str) or not body["environment"].strip():
        raise HTTPException(status_code=400, detail="`environment` must be a non-empty string")
    

    if not isinstance(body["services_to_deploy"], list) or not body["services_to_deploy"]:
        raise HTTPException(status_code=400, detail="`services_to_deploy` must be a non-empty list of strings") 
    
    # 3. Terraform path
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tf_path = os.path.join(BASE_DIR, "terraform", "create_ephemeral_backend")


    # 4a. Terraform init & apply

    try:

        print(body["environment"])
        subprocess.run(["terraform", "init"], cwd=tf_path, check=True)
        subprocess.run([
            "terraform", "import",
            "aws_iam_role.ecr_role",
            "ec2-ecr-access-role"
        ], cwd=tf_path, check=False)
        subprocess.run([
            "terraform", "import",
            "aws_iam_instance_profile.ecr_instance_profile",
            "ecr-instance-profile"
        ], cwd=tf_path, check=False)
        
        subprocess.run([
            "terraform", "apply", "-auto-approve",
            "-var", f'environment="{body["environment"]}"',  
            "-var", f"services_to_deploy={json.dumps(body["services_to_deploy"])}",
        ], cwd=tf_path, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Terraform execution failed: {e}")
    
    # 5a. Gather outputs
    outputs = get_terraform_outputs(tf_path)

    return {
        "status": "success",
        "message": "Ephemeral environment deployed to EC2 with Terraform",
        "instance_id": outputs["instance_id"],
        "instance_ip": outputs["instance_ip"]
    }
