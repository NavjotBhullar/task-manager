from pydantic import BaseModel

class Message(BaseModel):
    sender: str
    receiver: str
    content: str