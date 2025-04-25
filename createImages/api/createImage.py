import os
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
def get_endpoints():
    env = os.getenv("environment", "dev")
    endpoints = {
        f"servicio{i}": f"{env}.servicio{i}.midominio.com"
        for i in range(1, 6)
    }
    return JSONResponse(content=endpoints)