from app.models import ChatMessage, User
from datetime import datetime
from typing import Optional, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(user, db):
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    await db.users.insert_one(user_dict)
    return user_dict

async def get_user_by_username(username, db):
    return await db.users.find_one({"username": username})

async def ensure_indexes(db):
    await db.chat_messages.create_index("conversation_id")
    await db.chat_messages.create_index("user_id")
    await db.chat_messages.create_index("timestamp")
    await db.users.create_index("username", unique=True)

async def insert_chat_message(chat: ChatMessage, db):
    data = chat.dict()
    if 'timestamp' not in data or data['timestamp'] is None:
        data['timestamp'] = datetime.utcnow()
    await db.chat_messages.insert_one(data)

async def get_chat_messages(conversation_id: str, db, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, keywords: Optional[List[str]] = None):
    query = {"conversation_id": conversation_id}
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date
        if not query["timestamp"]:
            del query["timestamp"]
    if keywords:
        query["message"] = {"$regex": "|".join(keywords), "$options": "i"}
    cursor = db.chat_messages.find(query)
    return await cursor.to_list(length=None)

async def delete_chat_messages(conversation_id: str, db):
    await db.chat_messages.delete_many({"conversation_id": conversation_id})

async def get_user_chats(user_id: str, skip: int = 0, limit: int = 10, db=None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, keywords: Optional[List[str]] = None):
    query = {"user_id": user_id}
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date
        if not query["timestamp"]:
            del query["timestamp"]
    if keywords:
        query["message"] = {"$regex": "|".join(keywords), "$options": "i"}
    cursor = db.chat_messages.find(query).skip(skip).limit(limit)
    return await cursor.to_list(length=None) 