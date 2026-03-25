import os
from fastapi import FastAPI
from notif.router import router

app = FastAPI(
    title="Notification Service",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Notification Service is running"}


@app.get("/health")
async def health():
    port = int(os.getenv("PORT", 3004))
    return {
        "status": "healthy",
        "service": "notification-service",
        "port": port
    }