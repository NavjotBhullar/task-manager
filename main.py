from fastapi import FastAPI
from services.user.router import router

app = FastAPI(title="User Service")

app.include_router(router)

