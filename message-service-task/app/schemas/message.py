from pydantic import BaseModel
from typing import Optional

class MessageCreate(BaseModel):
    receiver: Optional[str] = None
    content: str
    group: Optional[str] = None