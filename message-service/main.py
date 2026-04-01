from bson import ObjectId
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi import UploadFile, File
from typing import List, Optional, Dict
from datetime import datetime
import httpx
import jwt
import os
from starlette.requests import Request
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

app = FastAPI(title="Message Service")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

#image upload
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.message_db

# Templates
templates = Jinja2Templates(directory="templates")

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

if not JWT_SECRET_KEY:
    raise ValueError("❌ JWT_SECRET_KEY not found!")

print(f"""
{'='*60}
🚀 MESSAGE SERVICE STARTING
{'='*60}
Auth Service: {AUTH_SERVICE_URL}
User Service: {USER_SERVICE_URL}
{'='*60}
""")

# ============== MODELS ==============

class LoginRequest(BaseModel):
    email: str
    password: str

class GroupCreate(BaseModel):
    name: str
    members: List[str]

# ============== CONNECTION MANAGER ==============

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ User {user_id} connected. Total: {len(self.active_connections)}")
        
        # Broadcast online users to everyone
        await self.broadcast_online_users()

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"❌ User {user_id} disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")
                return False
        return False

    async def broadcast_to_group(self, message: dict, group_members: List[str]):
        for member_id in group_members:
            await self.send_personal_message(message, member_id)

    async def broadcast_online_users(self):
        """Broadcast online users list to all connected users"""
        online_list = self.get_online_users()
        message = {"type": "online_users", "users": online_list}
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

    def get_online_users(self) -> List[str]:
        return list(self.active_connections.keys())

manager = ConnectionManager()

# ============== AUTH HELPER ==============

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# ============== ENDPOINTS ==============

@app.get("/", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    print(f"\n{'='*60}")
    print(f"📨 LOGIN: {credentials.email}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(
                f"{AUTH_SERVICE_URL}/auth/login",
                json={
                    "email": credentials.email,
                    "password": credentials.password
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                if not token:
                    raise HTTPException(status_code=500, detail="No token")
                
                payload = decode_token(token)
                user_id = payload.get("user_id")
                email = payload.get("email")
                
                print(f"✅ SUCCESS: {user_id}\n")
                
                return {
                    "access_token": token,
                    "user_id": str(user_id),
                    "email": email
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

@app.get("/users")
async def get_users(authorization: str = Header(None), token: str = Query(None)):
    auth_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.replace("Bearer ", "")
    elif token:
        auth_token = token
    
    if not auth_token:
        raise HTTPException(status_code=401, detail="No token")
    
    # Verify token
    decode_token(auth_token)
    
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get(
                f"{USER_SERVICE_URL}/users/public",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Got {len(users)} users")
                
                return [
                    {
                        "id": user.get("id"),
                        "email": user.get("email") or user.get("name"),
                        "full_name": user.get("name") or user.get("email") or "Unknown"
                    }
                    for user in users
                ]
            else:
                raise HTTPException(status_code=response.status_code, detail="User service error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")

@app.get("/users/online")
async def get_online_users():
    return {"online_users": manager.get_online_users()}

@app.post("/groups")
async def create_group(group: GroupCreate, token: str = Query(...)):
    payload = decode_token(token)
    user_id = str(payload.get("user_id"))
    
    members = list(set(group.members + [user_id]))
    
    group_data = {
        "name": group.name,
        "members": members,
        "created_by": user_id,
        "created_at": datetime.utcnow()
    }
    
    result = await db.message_groups.insert_one(group_data)
    print(f"✅ Group '{group.name}' created")
    
    return {
        "message": "Group created",
        "group_id": str(result.inserted_id),
        "name": group.name
    }

@app.get("/groups")
async def get_groups(token: str = Query(...)):
    payload = decode_token(token)
    user_id = str(payload.get("user_id"))
    
    groups = await db.message_groups.find({"members": user_id}).to_list(100)
    
    return [
        {
            "id": str(g["_id"]),
            "name": g["name"],
            "members": g["members"]
        }
        for g in groups
    ]

@app.get("/messages/history")
async def get_message_history(
    receiver_id: Optional[str] = None,
    group_id: Optional[str] = None,
    token: str = Query(...)
):
    payload = decode_token(token)
    user_id = str(payload.get("user_id"))

    # 👥 GROUP CHAT
    if group_id:
        query = {
            "group_id": group_id,
            "is_group": True
        }
        

    # 👤 DIRECT MESSAGE
    elif receiver_id:
        query = {
            "is_group": False,
            "$or": [
                {"sender_id": user_id, "receiver_id": receiver_id},
                {"sender_id": receiver_id, "receiver_id": user_id}
            ]
        }

    else:
        return []

    messages = await db.messages.find(query).sort("timestamp", 1).to_list(100)

    print(f"📜 Loaded {len(messages)} messages")

    return [
        {
            "sender_id": m["sender_id"],
            "receiver_id": m.get("receiver_id"),
            "group_id": str(m["group_id"]) if m.get("group_id") else None,
            "content": m.get("content"),
            "file_url": m.get("file_url"),          
            "msg_type": m.get("msg_type", "text"), 
            "timestamp": m["timestamp"].isoformat(),
            "is_group": m.get("is_group", False)
        }
        for m in messages
    ]

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/uploads/{file.filename}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id = None
    try:
        payload = decode_token(token)
        user_id = str(payload.get("user_id"))
        
        await manager.connect(user_id, websocket)
        
        while True:
            data = await websocket.receive_json()
            print(f"📩 Message from {user_id}: {data}")
            
            # Save to database
            message_data = {
              "sender_id": user_id,
              "receiver_id": data.get("receiver_id") if not data.get("is_group") else None,
              "group_id": data.get("group_id") if data.get("is_group") else None,
              "content": data.get("content"),
              "file_url": data.get("file_url"),   
              "msg_type": data.get("msg_type", "text"), 
              "timestamp": datetime.utcnow(),
              "is_group": data.get("is_group", False)
             }
            
            await db.messages.insert_one(message_data)
            
            # Prepare response
            response = {
                "type": "message",
                "sender_id": user_id,
                "receiver_id": data.get("receiver_id"),
                "group_id": data.get("group_id"),
                "content": data.get("content"),
                "file_url": data.get("file_url"),
                "msg_type": data.get("msg_type", "text"),
                "timestamp": message_data["timestamp"].isoformat(),
                "is_group": data.get("is_group", False)
            }
            
            if data.get("is_group"):
                # Group message
                from bson import ObjectId
                group = await db.message_groups.find_one({"_id": ObjectId(data["group_id"])})
                if group:
                    print(f"📤 Broadcasting to group: {group['name']}")
                    await manager.broadcast_to_group(response, group["members"])
            else:
                # Direct message
                receiver_id = data.get("receiver_id")
                print(f"📤 Sending DM: {user_id} → {receiver_id}")
                
                # Send to receiver
                sent_to_receiver = await manager.send_personal_message(response, receiver_id)
                print(f"   → Receiver ({receiver_id}): {'✅' if sent_to_receiver else '❌ offline'}")
                
                # Send to sender (echo)
                sent_to_sender = await manager.send_personal_message(response, user_id)
                print(f"   → Sender ({user_id}): {'✅' if sent_to_sender else '❌'}")
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
            await manager.broadcast_online_users()
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        if user_id:
            manager.disconnect(user_id)
            await manager.broadcast_online_users()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "message-service",
        "connections": len(manager.active_connections),
        "online_users": manager.get_online_users()
    }