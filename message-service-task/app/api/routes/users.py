from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from app.db.mongo import users_collection

router = APIRouter()


class User(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register_user(user: User):
    username = user.username.strip()
    password = user.password.strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        return {"message": "User already exists"}

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    result = await users_collection.insert_one(
        {"username": username, "password": hashed_password.decode("utf-8")}
    )

    return {
        "message": "User registered successfully",
        "id": str(result.inserted_id),
        "username": username,
    }


@router.get("/")
async def get_users():
    users = []

    async for user in users_collection.find({}, {"password": 0}):
        user["_id"] = str(user["_id"])
        users.append(user)

    return users
