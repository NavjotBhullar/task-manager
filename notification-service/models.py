from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class NotificationType(str,Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_OVERDUE = "task_overdue"


class NotificationStatus(str,Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"

#Request Models
class NotifyTaskRequest(BaseModel):
    notification_type : NotificationType = NotificationType.TASK_ASSIGNED
    recipient_email: Optional[EmailStr] = None
    recipient_user_id: Optional[str] = None

class BulkNotifyRequest(BaseModel):
    task_ids: list[str]
    notification_type : NotificationType = NotificationType.TASK_ASSIGNED
    recipient_user_ids: list[str]

