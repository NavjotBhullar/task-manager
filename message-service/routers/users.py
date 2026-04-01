from fastapi import APIRouter, Depends
import httpx
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

USER_SERVICE_URL = "http://127.0.0.1:8002"


@router.get("/")
async def get_users(user=Depends(get_current_user)):

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{USER_SERVICE_URL}/users")

    users = res.json()

    # remove current user
    return [u for u in users if u["id"] != user["user_id"]]