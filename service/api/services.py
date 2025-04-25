from fastapi import APIRouter
from service.data.constants import AVAILABLE_SERVICES

router = APIRouter()

@router.get("/")
async def get_services():
    return {"services": AVAILABLE_SERVICES}
