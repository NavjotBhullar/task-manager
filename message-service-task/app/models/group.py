from pydantic import BaseModel
from typing import List

class Group(BaseModel):
    name: str
    members: List[str]