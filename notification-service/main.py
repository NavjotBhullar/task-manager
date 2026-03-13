import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from notif.queue import queue_worker
from notif.router import router

# FastAPI application with a lifespan event to start the queue worker
# The queue worker will run in the background and process notification tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(queue_worker())
    yield
    worker_task.cancel()

app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Notification Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy","service":"notification-service", "port": 3004}