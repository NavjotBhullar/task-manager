from fastapi import FastAPI

app = FastAPI(
    title="Task Service",
    version="1.0"
)

@app.get("/")
async def health():
    return {"service": "task-service running"}