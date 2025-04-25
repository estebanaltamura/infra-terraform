from fastapi import APIRouter
from service.data.constants import AVAILABLE_STABLE_ENVIRONMENTS

router = APIRouter()

@router.get("/")
async def get_stable_environments():
    return {"available_stable_environments": AVAILABLE_STABLE_ENVIRONMENTS}
