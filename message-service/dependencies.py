from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import httpx
import os

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")


async def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AUTH_SERVICE_URL}/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401)

    return resp.json()