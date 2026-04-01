from datetime import datetime

def message_schema(msg):
    return {
        "id": str(msg["_id"]),
        "sender_id": msg["sender_id"],
        "receiver_id": msg.get("receiver_id"),
        "group_id": str(msg["group_id"]) if msg.get("group_id") else None,
        "content": msg["content"],
        "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else msg["timestamp"],
        "is_group": msg.get("is_group", False)
    }