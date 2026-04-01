from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId

from database import messages_collection
from dependencies import get_current_user
from models import message_schema
from schemas import MessageCreate

router = APIRouter(prefix="/messages", tags=["Messages"])


# =========================================================
# SEND MESSAGE (USER or GROUP)
# =========================================================
@router.post("/send")
async def send_message(
    data: MessageCreate,
    user=Depends(get_current_user)
):

    # Validation
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not data.receiver_id and not data.group_id:
        raise HTTPException(status_code=400, detail="Provide receiver_id or group_id")

    msg = {
        "sender_id": user["user_id"],
        "receiver_id": data.receiver_id,
        "group_id": ObjectId(data.group_id) if data.group_id else None,
        "content": data.content,
        "timestamp": datetime.utcnow(),
        "is_group": bool(data.group_id)
    }

    result = await messages_collection.insert_one(msg)
    msg["_id"] = result.inserted_id

    return message_schema(msg)


# =========================================================
# GET USER CHAT HISTORY (1-to-1)
# =========================================================
@router.get("/history/user/{user_id}")
async def get_user_history(
    user_id: str,
    user=Depends(get_current_user)
):

    cursor = messages_collection.find({
        "$or": [
            {"sender_id": user["user_id"], "receiver_id": user_id},
            {"sender_id": user_id, "receiver_id": user["user_id"]}
        ]
    }).sort("timestamp", 1)   # ✅ IMPORTANT

    return [message_schema(m) async for m in cursor]


# =========================================================
# GET GROUP CHAT HISTORY
# =========================================================
@router.get("/history/group/{group_id}")
async def get_group_history(
    group_id: str,
    user=Depends(get_current_user)
):

    try:
        obj_id = ObjectId(group_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid group_id")

    cursor = messages_collection.find({
        "group_id": obj_id
    }).sort("timestamp", 1)

    return [message_schema(m) async for m in cursor]