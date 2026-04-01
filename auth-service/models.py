from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name:str
    email:EmailStr
    password: str = Field(
         min_length=6,
         max_length=72
    )

class LoginRequest(BaseModel):
    email: str
    password: str    
    
class RefreshRequest(BaseModel):
    refresh_token: str
   
   
