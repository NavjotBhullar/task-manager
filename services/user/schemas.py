from pydantic import BaseModel
from typing import Optional,List

class UserProfile(BaseModel):
    name:str
    avatar:Optional[str]  = None

class UserCreate(BaseModel):
    email:str
    profile: UserProfile
    role:Optional[str] =None

class UserUpdate(BaseModel):
    profile: Optional[UserProfile] = None
    role: Optional[str] = None

class TaskAssign(BaseModel):
    title: str
    description: Optional[str] = None


class UserResponse(BaseModel):
    id:str
    email:str
    profile:UserProfile
    role:str
    task_ids: List[str]

class Config:
    populate_by_name = True