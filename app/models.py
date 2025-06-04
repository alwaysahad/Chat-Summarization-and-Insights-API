from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatMessage(BaseModel):
    conversation_id: str
    user_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    username: str
    hashed_password: str 