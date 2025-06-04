from fastapi import APIRouter, HTTPException, Depends, Query
from app.crud import get_user_chats, create_user, get_user_by_username, verify_password
from app.database import get_db
from app.schemas import UserCreate, UserLogin
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

@router.post("/auth/register")
async def register(user: UserCreate, db=Depends(get_db)):
    existing = await get_user_by_username(user.username, db)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    await create_user(user, db)
    return {"message": "User registered successfully"}

@router.post("/auth/login")
async def login(user: UserLogin, db=Depends(get_db)):
    db_user = await get_user_by_username(user.username, db)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/{user_id}/chats", response_model=list)
async def get_user_chat_history(
    user_id: str,
    page: int = 1,
    limit: int = 10,
    db=Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    keywords: Optional[str] = Query(None)
):
    skip = (page - 1) * limit
    keyword_list = keywords.split(",") if keywords else None
    chats = await get_user_chats(user_id, skip, limit, db, start_date, end_date, keyword_list)
    if not chats:
        raise HTTPException(status_code=404, detail="No chats found for this user")
    for chat in chats:
        chat.pop('_id', None)
        # Ensure timestamp exists and is a datetime object
        if 'timestamp' not in chat or chat['timestamp'] is None:
            chat['timestamp'] = datetime.utcnow()
        elif not isinstance(chat['timestamp'], datetime):
            try:
                chat['timestamp'] = datetime.fromisoformat(chat['timestamp'])
            except Exception:
                chat['timestamp'] = datetime.utcnow()
    return chats 