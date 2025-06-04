from pydantic import BaseModel
from datetime import datetime

class ChatMessageCreate(BaseModel):
    conversation_id: str
    user_id: str
    message: str

class ChatMessageResponse(BaseModel):
    conversation_id: str
    user_id: str
    message: str
    timestamp: datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str 