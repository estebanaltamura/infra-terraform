from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv




load_dotenv()  # Carga variables desde .env automáticamente
router = APIRouter()

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


@router.get("/branches")
async def get_repo_branches():
    url = f"https://api.github.com/repos/{GITHUB_USER}/lonely-barcelona/branches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        branches = [b["name"] for b in data]
        return {"branches": branches}
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
