from fastapi import APIRouter
from app.schemas.message import MessageCreate
from app.db.mongo import messages_collection
from app.db.redis import redis_client
import json

router = APIRouter()


@router.post("/")
async def send_message(sender: str, message: MessageCreate):
    msg = {
        "type": "personal",
        "sender": sender,
        "receiver": message.receiver,
        "content": message.content,
    }

    result = await messages_collection.insert_one(msg)

    msg["_id"] = str(result.inserted_id)

    redis_client.publish("chat", json.dumps(msg))

    return {"msg": "sent"}


@router.get("/history")
async def get_messages(user1: str, user2: str):
    messages = await messages_collection.find(
        {
            "type": "personal",
            "$or": [
                {"sender": user1, "receiver": user2},
                {"sender": user2, "receiver": user1},
            ],
        }
    ).to_list(100)

    for m in messages:
        m["_id"] = str(m["_id"])

    return messages


@router.post("/group")
async def send_group_message(sender: str, message: dict):
    msg = {
        "type": "group",
        "sender": sender,
        "group": message["group"],
        "content": message["content"],
    }

    result = await messages_collection.insert_one(msg)

    msg["_id"] = str(result.inserted_id)

    redis_client.publish("chat", json.dumps(msg))

    return {"msg": "group message sent"}


@router.get("/group/{group_name}")
async def get_group_messages(group_name: str):
    messages = await messages_collection.find(
        {"type": "group", "group": group_name}
    ).to_list(100)

    for m in messages:
        m["_id"] = str(m["_id"])

    return messages
