from fastapi import Header, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

from .config import MONGO_URI, AUTH_SERVICE_URL

client = AsyncIOMotorClient(MONGO_URI)

db = client.tasks_db


async def get_db():

    return db


async def get_current_user(authorization: str = Header(...)):

    token = authorization.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            f"{AUTH_SERVICE_URL}/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )

    if resp.status_code != 200:

        raise HTTPException(status_code=401, detail="Invalid token")

    return resp.json()["user"]