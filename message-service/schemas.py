from pydantic import BaseModel
from typing import Optional,List


class MessageCreate(BaseModel):
    content: str
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None

class GroupCreate(BaseModel):
    name: str
    members: List[str]

class AddUser(BaseModel):
    group_id: str
    user_id: str