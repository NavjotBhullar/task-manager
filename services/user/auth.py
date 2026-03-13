import httpx,os
from fastapi import Header, HTTPException


AUTH_URL = os.getenv("AUTH_SERVICE_URL")

async def validate_token(authorization: str = Header(...)):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            AUTH_URL,
            headers={"Authorization": authorization}
        )

    if response.status_code !=200:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    return response.json()