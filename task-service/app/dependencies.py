from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os

security = HTTPBearer()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.tasks_db


async def get_db():
    return db


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AUTH_SERVICE_URL}/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = resp.json()

    if not data.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "id": data["user_id"],
        "email": data["email"]
    }