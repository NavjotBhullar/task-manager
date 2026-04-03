from fastapi import FastAPI
from routes.scraper_routes import router

app = FastAPI(title="Navjot Scraper Service")

app.include_router(router, prefix="/scraper")


@app.get("/")
def root():
    return {"message": "Scraper Service is Live"}