from fastapi import APIRouter
from fastapi.requests import Request

router = APIRouter()

@router.post("/")
async def create_no_ephemeral_backend(request: Request):
    return {"stable environment status": 'creating'}
