from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.websocket_manager import manager
from app.services.redis_pubsub import start_redis_listener

from app.api.routes import auth, users, messages, groups

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(messages.router, prefix="/messages")
app.include_router(groups.router, prefix="/groups")


@app.on_event("startup")
def startup():
    start_redis_listener()


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse( request,"register.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request, "chat.html", {"request": request})


@app.get("/groups-page", response_class=HTMLResponse)
async def group_page(request: Request):
    return templates.TemplateResponse(request, "groups.html", {"request": request})


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            await manager.send_personal_message(data["receiver"], data)

    except:
        manager.disconnect(user_id, websocket)
