from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import Optional
from bson import ObjectId

from database import notifications_collection,tasks_collection,users_collection
from models import NotifyTaskRequest, NotificationStatus, NotificationType, BulkNotifyRequest
from utils import verify_token, build_email_content, send_email
from notif.dependencies import get_current_user
from notif.queue import notification_queue

router = APIRouter(prefix="/notify", tags=["Notifications"])

# Convert ObjectId to string for JSON serialization
def serialize(doc: dict) -> dict: 
    doc["_id"] = str(doc["_id"])
    return doc

@router.post("/task/{task_id}", status_code=status.HTTP_202_ACCEPTED)
async def notify_task(task_id: str, request: NotifyTaskRequest, user = Depends(get_current_user)):

    # 1. Fetch task details for email content
    try:
        task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    except Exception:
        task = None
    task = task or {"_id": task_id, "title": f"Task {task_id}","due_date": "N/A" }

    # 2. Determine recipient email
    recipient_email = request.recipient_email
    user_name = "User"
    user_id = request.recipient_user_id or user.get("user_id","")

    if not recipient_email:
        try:
            db_user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if  db_user:
                recipient_email = db_user.get("email")
                user_name = db_user.get("name",db_user.get("username","User"))
        except Exception:
            pass

    if  not recipient_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipient email or user ID is required")
    
    # 3. Build notification content + store
    subject, html_body = build_email_content(request.notification_type, task, user_name)

    doc = {
        "task_id": task_id,
        "user_id": user_id,
        "recipient_email": recipient_email,
        "notification_type": request.notification_type,
        "status": NotificationStatus.PENDING,
        "subject": subject,
        "body": html_body,
        "retry_count": 0,
        "error_message": None,
        "created_at": datetime.utcnow(),
        "sent_at": None
    }

    result = await notifications_collection.insert_one(doc)
    notification_id = str(result.inserted_id)

    # 4. Enqueue notification for async sending
    await notification_queue.put(notification_id)

    return {
        "message": "Notification queued successfully",
        "notification_id": notification_id,
        "status": NotificationStatus.QUEUED,
        "recipient_email": recipient_email
    }

@router.get("/status")
async def get_all_notifications(
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    limit: int = 20,
    skip: int = 0,
    user = Depends(get_current_user)
):
    query = {}
    if status:
        query["status"] = status
    if notification_type:
        query["notification_type"] = notification_type

    total = await notifications_collection.count_documents(query)
    cursor = notifications_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)

    return {
        "total": total,
        "notifications": [serialize(doc) for doc in docs]
    }

@router.get("/status/{notification_id}")
async def get_notification_status(notification_id: str, user = Depends(get_current_user)):
    try:
        doc = await notifications_collection.find_one({"_id": ObjectId(notification_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification ID")
    
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    return serialize(doc)

@router.get("/task/{task_id}/history")
async def task_notification_history(task_id: str, user = Depends(get_current_user)):
    docs = await notifications_collection.find({"task_id": task_id}).sort("created_at", -1).to_list(length=50)
    return {
        "total": len(docs),
        "notifications": [serialize(d) for d in docs]
    }

@router.post("/bulk")
async def bulk_notify(request: BulkNotifyRequest, user = Depends(get_current_user)):
    queued_ids = []

    for task_id,user_id in zip(request.task_ids,request.recipient_user_ids):
        try:
            db_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            continue

        if not db_user or not db_user.get("email"):
            continue

        try:
            task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
        except Exception:
            task = None
        task = task or {"_id": task_id, "title": f"Task {task_id}" }

        subject, html_body = build_email_content(request.notification_type, task, db_user.get("name","User"))

        doc = {
            "task_id": task_id,
            "user_id": user_id,
            "recipient_email": db_user["email"],
            "notification_type": request.notification_type,
            "status": NotificationStatus.PENDING,
            "subject": subject,
            "body": html_body,
            "retry_count": 0,
            "error_message": None,
            "created_at": datetime.utcnow(),
            "sent_at": None
        }

        result = await notifications_collection.insert_one(doc)
        notification_id = str(result.inserted_id)
        await notification_queue.put(notification_id)
        queued_ids.append(notification_id)

    return {
        "message": "Bulk notifications queued",
        "queued_count": len(queued_ids),
        "notification_ids": queued_ids
    }

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, user = Depends(get_current_user)):
    try:
        result = await notifications_collection.delete_one({"_id": ObjectId(notification_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    return {"message": "Notification deleted successfully"}

